#!/usr/bin/env python3
"""
X-Research Main Orchestrator
Flat output mode: generates a single .md file per research topic.

Flow: Data collection (X + Web) → Agent synthesis → Single .md report
"""

import os
import sys
import time
import json
import logging
import tempfile
from pathlib import Path
from datetime import datetime
import click
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.utils import setup_logging, slugify, ensure_dir
from scripts.x_research import run_x_research
from scripts.web_research import run_web_research
from scripts.report import generate_report


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    config_file = Path(__file__).parent.parent / config_path
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)


@click.command()
@click.option('--topic', required=True, help='Research topic/keyword')
@click.option('--tweet-limit', type=int, help='Max tweets to analyze')
@click.option('--web-sources', type=int, help='Max web sources to crawl')
@click.option('--config', default='config.yaml', help='Config file path')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--skip-to-stage', type=int, default=0, help='Skip to stage (1-4)')
def main(topic: str, tweet_limit: int, web_sources: int,
         config: str, debug: bool, skip_to_stage: int):
    """
    X-Research: Deep research → single .md report (Hermes Agent mode).

    Examples:
        python main.py --topic "Ethereum L2 2026"
        python main.py --topic "Perp DEX" --skip-to-stage 4
    """
    start_time = time.time()
    os.environ["HERMES_MODE"] = "true"

    cfg = load_config(config)

    if tweet_limit:
        cfg['research']['tweet_limit'] = tweet_limit
    if web_sources:
        cfg['research']['web_sources'] = web_sources
    if debug:
        cfg['debug']['enabled'] = True
        cfg['logging']['level'] = 'DEBUG'

    log_level = cfg['logging']['level']
    logger = setup_logging(log_level)

    logger.info(f"X-Research: {topic}")
    logger.info("Mode: Hermes Agent")

    # Single output file path
    topic_slug = slugify(topic)
    date_str = datetime.now().strftime(cfg['output']['date_format'])
    filename = cfg['output']['filename_pattern'].format(
        topic_slug=topic_slug,
        date=date_str
    )
    report_path = Path(cfg['output']['report_dir']) / filename
    ensure_dir(report_path.parent)

    # Temp dir for intermediate data
    temp_dir_env = os.getenv("XRESEARCH_TEMP_DIR")
    if temp_dir_env and Path(temp_dir_env).exists():
        temp_dir = Path(temp_dir_env)
    elif skip_to_stage > 1:
        import glob
        candidates = sorted(glob.glob("/tmp/x-research-*"), key=os.path.getmtime, reverse=True)
        temp_dir = Path(candidates[0]) if candidates else Path(tempfile.mkdtemp(prefix="x-research-"))
    else:
        temp_dir = Path(tempfile.mkdtemp(prefix="x-research-"))
    os.environ["XRESEARCH_TEMP_DIR"] = str(temp_dir)

    logger.info(f"Output: {report_path}")
    logger.info(f"Temp: {temp_dir}")

    try:
        synthesis_result = {}
        tweets_data = []
        web_data = []

        # ============================================================
        # RESUME: Load cached data if skipping stages
        # ============================================================
        if skip_to_stage > 1:
            tweets_path = temp_dir / "tweets.json"
            if tweets_path.exists():
                with open(tweets_path) as f:
                    tweets_data = json.load(f)
                logger.info(f"Loaded {len(tweets_data)} tweets from cache")

        if skip_to_stage > 2:
            web_path = temp_dir / "web_sources.json"
            if web_path.exists():
                with open(web_path) as f:
                    web_data = json.load(f)
                logger.info(f"Loaded {len(web_data)} web sources from cache")

        # ============================================================
        # STAGE 1: X Research
        # ============================================================
        if skip_to_stage <= 1:
            logger.info("=" * 50)
            logger.info("STAGE 1: X Research")
            logger.info("=" * 50)

            s1 = time.time()
            tweets_data = run_x_research(
                topic=topic,
                config=cfg,
                output_path=temp_dir / "tweets.json"
            )
            logger.info(f"Stage 1: {time.time() - s1:.1f}s | {len(tweets_data)} tweets")

        # ============================================================
        # STAGE 2: Web Research
        # ============================================================
        if skip_to_stage <= 2:
            logger.info("=" * 50)
            logger.info("STAGE 2: Web Research")
            logger.info("=" * 50)

            s2 = time.time()
            web_data = run_web_research(
                topic=topic,
                config=cfg,
                output_path=temp_dir / "web_sources.json"
            )
            logger.info(f"Stage 2: {time.time() - s2:.1f}s | {len(web_data)} sources")

        # ============================================================
        # STAGE 3: Agent Synthesis
        # ============================================================
        synthesis_path = temp_dir / "synthesis.json"

        if synthesis_path.exists():
            logger.info("Loading agent synthesis...")
            with open(synthesis_path) as f:
                synthesis_result = json.load(f)
        else:
            logger.info("=" * 50)
            logger.info("STAGE 3: Agent Synthesis")
            logger.info("=" * 50)

            prompt = build_hermes_prompt(topic, tweets_data, web_data)
            prompt_file = temp_dir / "HERMES_SYNTHESIS_PROMPT.md"
            with open(prompt_file, 'w') as f:
                f.write(prompt)

            print(f"\n{'='*50}")
            print("  AGENT SYNTHESIS REQUIRED")
            print(f"{'='*50}")
            print(f"\n  Tweets: {len(tweets_data)} | Web: {len(web_data)}")
            print(f"\n  Prompt: {prompt_file}")
            print(f"\n  Next: Write synthesis.json to {temp_dir}")
            print(f"  Then: python main.py --topic '{topic}' --skip-to-stage 4")
            print(f"{'='*50}\n")

            return 42

        # ============================================================
        # STAGE 4: Report Generation (single .md file)
        # ============================================================
        logger.info("=" * 50)
        logger.info("STAGE 4: Report Generation")
        logger.info("=" * 50)

        s4 = time.time()
        generate_report(
            topic=topic,
            synthesis_result=synthesis_result,
            tweets_data=tweets_data,
            web_data=web_data,
            config=cfg,
            output_path=report_path
        )
        logger.info(f"Stage 4: {time.time() - s4:.1f}s")

        # Cleanup temp files
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        logger.debug(f"Cleaned up: {temp_dir}")

        # Summary
        total = time.time() - start_time
        logger.info("=" * 50)
        logger.info("DONE")
        logger.info("=" * 50)
        logger.info(f"Report: {report_path}")
        logger.info(f"Total: {total:.1f}s ({total/60:.1f}m)")

        # Telegram
        if cfg['telegram']['enabled']:
            from lib.utils import send_telegram_brief
            send_telegram_brief(report_path=report_path, config=cfg)

        return 0

    except Exception as e:
        logger.error(f"Failed: {e}", exc_info=True)
        return 1


def build_hermes_prompt(topic: str, tweets_data: list, web_data: list) -> str:
    """Build detailed synthesis prompt for agent (VIETNAMESE output)."""
    lines = [
        f"# X-Research: Tổng hợp sâu — {topic}",
        "",
        "## Nhiệm vụ",
        f"Bạn là chuyên gia phân tích crypto. Phân tích TOÀN BỘ dữ liệu dưới đây và viết một báo cáo nghiên cứu chi tiết về **{topic}**.",
        "Đầu ra phải là JSON hợp lệ với nội dung phong phú, bằng **tiếng Việt**.",
        "",
        "## NGUYÊN TẮC QUAN TRỌNG",
        "- KHÔNG liệt kê raw tweet hay raw web excerpt trong output.",
        "- KHÔNG viết section 'Nguồn' hay 'Sources'.",
        "- TẤT CẢ insight phải được TỔNG HỢP, PHÂN TÍCH, và KẾT NỐI thành narrative mạch lạc.",
        "- Dùng tweet và web data làm CONTEXT để viết analysis, KHÔNG phải để copy-paste.",
        "",
        "## Cấu trúc JSON yêu cầu",
        "```json",
        "{",
        '  "executive_summary": "4-5 câu tóm tắt: quy mô thị trường, key players, diễn biến gần đây, triển vọng",',
        '  "market_landscape": {',
        '    "leaders": ["dẫn đầu + lý do cụ thể"],',
        '    "challengers": ["thử thách + điểm khác biệt"],',
        '    "total_addressable_market": "ước tính hoặc xu hướng"',
        '  },',
        '  "deep_analysis": "2500-3500 từ tiếng Việt. Cấu trúc với heading rõ ràng: 1. Tổng quan thị trường, 2. Các bên chính & Định vị, 3. Diễn biến & Catalyst gần đây, 4. Xu hướng công nghệ, 5. Bối cảnh pháp lý, 6. Rủi ro & Thách thức. Mỗi claim PHẢI trích dẫn nguồn (@handle cho tweet, domain cho web). Đưa số liệu cụ thể (TVL, volume, funding, user) khi có.",',
        '  "key_metrics": {',
        '    "volume": "con số cụ thể hoặc xu hướng",',
        '    "market_share": "tỷ lệ nếu biết",',
        '    "funding": "các vòng gọi vốn gần đây",',
        '    "user_growth": "xu hướng DAU/MAU"',
        '  },',
        '  "emerging_trends": ["5-7 xu hướng cụ thể có ngữ cảnh"],',
        '  "contrarian_views": ["3-4 luận điểm bearish có bằng chứng"],',
        '  "information_gaps": ["dữ liệu nào còn thiếu / chưa chắc chắn"],',
        '  "alpha_signals": ["tín hiệu sớm hoặc cơ hội bị bỏ qua"]',
        '  },',
        "  \"metadata\": {",
        '    "tweet_count": N,',
        '    "web_source_count": N,',
        '    "model": "Hermes Agent"',
        "  }",
        "}",
        "```",
        "",
        "## Hướng dẫn viết",
        "- ĐỘ SÂU: 2500-3500 từ tối thiểu cho deep_analysis",
        "- TRÍCH DẪN: Mỗi claim cần nguồn. Dùng inline citations dạng [@author] hoặc [domain.com]",
        "- SỐ LIỆU: Trích xuất và highlight mọi metric (TVL, volume, funding, user count)",
        "- CÂN BẰNG: Bao gồm cả góc nhìn bullish và bearish",
        "- CỤ THỂ: Nêu tên. Đừng nói 'một số nền tảng' — hãy nói Hyperliquid, dYdX...",
        "- GAPS: Nêu rõ thông tin nào còn thiếu hoặc không chắc chắn",
        "- NGÔN NGỮ: Tiếng Việt chuyên ngành crypto, có thể dùng từ borrow từ tiếng Anh khi cần",
        "",
        "---",
        "",
        "## DỮ LIỆU ĐẦU VÀO (CHỈ DÙNG LÀM CONTEXT)",
        "",
    ]

    for t in tweets_data[:15]:
        text = t.get('text', '')[:150]
        lines.append(f"- **@{t.get('author', 'unknown')}**: {text}...")

    if len(tweets_data) > 15:
        lines.append(f"- ... and {len(tweets_data) - 15} more")

    lines.extend(["", "### Web Sources"])
    for s in web_data:
        title = s.get('title', 'Untitled')
        url = s.get('url', '')
        content = s.get('markdown', '')[:200]
        lines.append(f"- **{title}** ({url})")
        lines.append(f"  {content}...")

    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
