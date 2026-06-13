#!/usr/bin/env python3
"""
Trading Scheduler - Manages Lite and Full modes
- Full mode: 07:00 daily (Technical Analyst)
- Lite mode: Every minute (price monitoring)
"""
import asyncio
import sys
import subprocess
from pathlib import Path
from datetime import datetime, time
from typing import Optional
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()

from utils import setup_logging, get_logger, config
from utils.process_lock import ProcessLock
from utils.log_rotation import rotate_all


setup_logging("INFO")
logger = get_logger(__name__)


class TradingScheduler:
    """Scheduler for Lite and Full trading modes"""

    def __init__(self):
        self.running = False
        self.lite_process: Optional[subprocess.Popen] = None
        self.full_process: Optional[subprocess.Popen] = None

        # Load config
        default_config = config.load_default_params()
        scheduler_config = default_config.get('scheduler', {})
        runtime_config = default_config.get('runtime', {})

        # Full mode schedule (07:00 daily)
        self.full_mode_time = scheduler_config.get('full_mode_time', '07:00')
        self.full_mode_hour, self.full_mode_minute = map(int, self.full_mode_time.split(':'))

        # Lite mode runs continuously
        self.lite_mode_enabled = scheduler_config.get('lite_mode_enabled', True)

        # Daily report time (23:00)
        self.report_time = scheduler_config.get('report_time', '23:00')
        self.report_hour, self.report_minute = map(int, self.report_time.split(':'))

        # Runtime guard settings
        self.prevent_duplicate_instances = runtime_config.get(
            'prevent_duplicate_instances', True
        )
        self.lock_path = runtime_config.get(
            'lock_file', 'logs/run_paper_trading.lock'
        )
        self.full_lock = ProcessLock(path=self.lock_path, name="trading-runtime")

        # Track last execution
        self.last_full_run: Optional[datetime] = None
        self.last_report_run: Optional[datetime] = None
        self.last_full_skipped: Optional[datetime] = None
        self.last_report_skipped: Optional[datetime] = None

    def _full_runtime_active(self) -> tuple:
        """Return (active, holder_info)."""
        if not self.prevent_duplicate_instances:
            return False, None
        info = self.full_lock.lock_info()
        if info and info.get("pid_alive"):
            return True, info
        return False, info

    def _rotate_logs(self):
        try:
            cfg = config.load_default_params()
            results = rotate_all(cfg, project_root=project_root)
            for r in results:
                if r.get("rotated"):
                    logger.info(
                        f"Rotated log {r['path']} (size before {r['size_before']} bytes)"
                    )
        except Exception as e:
            logger.warning(f"Log rotation failed: {e}")

    def start_lite_mode(self):
        """Start Lite Mode Monitor"""
        if self.lite_process and self.lite_process.poll() is None:
            logger.info("Lite Mode already running")
            return

        logger.info("Starting Lite Mode Monitor...")

        script_path = project_root / "scripts" / "lite_mode_monitor.py"
        log_path = project_root / "logs" / "lite_mode.log"

        self.lite_process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdout=open(log_path, 'a'),
            stderr=subprocess.STDOUT,
            start_new_session=True
        )

        logger.info(f"✓ Lite Mode started (PID: {self.lite_process.pid})")

    def stop_lite_mode(self):
        """Stop Lite Mode Monitor"""
        if self.lite_process and self.lite_process.poll() is None:
            logger.info(f"Stopping Lite Mode (PID: {self.lite_process.pid})...")
            self.lite_process.terminate()
            try:
                self.lite_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.lite_process.kill()
            logger.info("✓ Lite Mode stopped")

    def run_full_mode(self):
        """Run Full Mode (Technical Analyst).

        Skip if a live runtime lock is already held (Phase 9A.2 guard).
        """
        logger.info("Starting Full Mode (Technical Analyst)...")

        active, holder = self._full_runtime_active()
        if active:
            pid = holder.get("pid") if holder else "?"
            started = holder.get("started_at", "?") if holder else "?"
            logger.warning(
                f"Scheduler: runtime already active at PID {pid} "
                f"(started={started}), skipping launch."
            )
            self.last_full_skipped = datetime.now()
            return None

        script_path = project_root / "scripts" / "run_paper_trading.py"
        log_path = project_root / "logs" / "full_mode.log"

        # Run in background
        process = subprocess.Popen(
            [sys.executable, str(script_path), "--single-cycle"],
            stdout=open(log_path, 'a'),
            stderr=subprocess.STDOUT,
            start_new_session=True
        )

        logger.info(f"✓ Full Mode started (PID: {process.pid})")
        self.last_full_run = datetime.now()

        return process

    def generate_daily_report(self):
        """Generate daily report"""
        logger.info("Generating daily report...")

        active, holder = self._full_runtime_active()
        if active:
            pid = holder.get("pid") if holder else "?"
            logger.warning(
                f"Scheduler: runtime active at PID {pid}; "
                f"daily report will still proceed (independent task)."
            )

        script_path = project_root / "scripts" / "generate_daily_report.py"
        log_path = project_root / "logs" / "daily_report.log"

        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdout=open(log_path, 'a'),
            stderr=subprocess.STDOUT,
            start_new_session=True
        )

        logger.info(f"✓ Daily report generation started (PID: {process.pid})")
        self.last_report_run = datetime.now()

        return process
    
    def should_run_full_mode(self) -> bool:
        """Check if Full Mode should run"""
        now = datetime.now()
        
        # Check if it's the right time
        if now.hour != self.full_mode_hour or now.minute != self.full_mode_minute:
            return False
        
        # Check if already ran today
        if self.last_full_run:
            if self.last_full_run.date() == now.date():
                return False
        
        return True
    
    def should_generate_report(self) -> bool:
        """Check if daily report should be generated"""
        now = datetime.now()
        
        # Check if it's the right time
        if now.hour != self.report_hour or now.minute != self.report_minute:
            return False
        
        # Check if already generated today
        if self.last_report_run:
            if self.last_report_run.date() == now.date():
                return False
        
        return True
    
    async def run(self):
        """Main scheduler loop"""
        self.running = True

        logger.info("=" * 80)
        logger.info("Trading Scheduler Started")
        logger.info("=" * 80)
        logger.info(f"Full Mode: Daily at {self.full_mode_time}")
        logger.info(f"Lite Mode: {'Enabled' if self.lite_mode_enabled else 'Disabled'}")
        logger.info(f"Daily Report: {self.report_time}")
        logger.info(f"Duplicate-instance guard: {'on' if self.prevent_duplicate_instances else 'off'}")
        logger.info("=" * 80)

        # Initial log rotation
        self._rotate_logs()

        # Start Lite Mode if enabled
        if self.lite_mode_enabled:
            self.start_lite_mode()

        try:
            while self.running:
                now = datetime.now()

                # Check if Full Mode should run
                if self.should_run_full_mode():
                    logger.info(f"⏰ Scheduled Full Mode at {now.strftime('%H:%M')}")
                    self.run_full_mode()

                # Check if daily report should be generated
                if self.should_generate_report():
                    logger.info(f"📊 Scheduled Daily Report at {now.strftime('%H:%M')}")
                    self.generate_daily_report()

                # Check if Lite Mode is still running
                if self.lite_mode_enabled and self.lite_process:
                    if self.lite_process.poll() is not None:
                        logger.warning("Lite Mode process died, restarting...")
                        self.start_lite_mode()

                # Periodic log rotation (once per loop iteration)
                self._rotate_logs()

                # Sleep for 30 seconds before next check
                await asyncio.sleep(30)

        except asyncio.CancelledError:
            logger.info("Scheduler cancelled")

        finally:
            self.stop_lite_mode()
            logger.info("Scheduler stopped")
    
    def stop(self):
        """Stop the scheduler"""
        logger.info("Stop signal received")
        self.running = False


async def main():
    """Main entry point"""
    scheduler = TradingScheduler()
    
    # Setup signal handlers
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}")
        scheduler.stop()
    
    import signal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await scheduler.run()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
