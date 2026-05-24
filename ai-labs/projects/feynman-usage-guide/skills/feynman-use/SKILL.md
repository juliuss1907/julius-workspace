---
description: Hướng dẫn sử dụng Feynman CLI cho research tasks
category: tools
version: 1.0
created: 2026-05-23
---

# Feynman Use Skill

## Khi nào dùng?

Khi Julius yêu cầu chạy Feynman CLI để nghiên cứu một topic.

## Cú pháp cơ bản

### Quick run (đã có alias)

```bash
fr --prompt "Research về [TOPIC], trình bày bằng tiếng Việt"
```

### Full command

```bash
cd ~/julius-workspace/personal/researchs
feynman --cwd . --prompt "Research về [TOPIC], trình bày bằng tiếng Việt"
```

## Workflow chuẩn

### 1. Tạo research plan (Feynman tự động)

Feynman sẽ:
- Tạo plan trong `outputs/.plans/<slug>.md`
- Ghi vào `CHANGELOG.md` nếu là project dài hạn

### 2. Đọc và gửi tóm tắt cho Julius

**MUST DO**: Đọc plan từ file và gửi tóm tắt qua telegram. **KHÔNG** tự động approve.

```bash
# Đọc plan
read_file ~/julius-workspace/personal/researchs/outputs/.plans/<slug>.md

# Gửi tóm tắt qua telegram
curl -X POST ...  # hoặc dùng send_message tool
```

### 3. Chờ Julius confirm

- Nếu Julius đồng ý: gửi "yes" cho Feynman
- Nếu Julius từ chối: gửi "no" hoặc kill process

### 4. Sau khi hoàn thành

- File output: `outputs/<slug>-report.md` hoặc `outputs/<slug>-brief.md`
- Đọc file và gửi tóm tắt qua telegram
- Lưu vào MemPalace nếu cần

## Quy tắc bắt buộc

### Language
- **Luôn thêm**: `, trình bày bằng tiếng Việt` vào cuối prompt
- **Ngoại lệ**: Chỉ khi Julius chỉ định ngôn ngữ khác

### Output location
- **Mặc định**: `~/julius-workspace/personal/researchs/`
- Sử dụng `--cwd .` để đảm bảo output đúng folder

### Interactive only
- **KHÔNG** chạy Feynman trong cron/background (nohup, tmux, pty)
- Chỉ chạy trong interactive terminal

### Cost awareness
- GPT-4 class: $0.5-2/giao dịch
- Monitor token usage trong file output

## Ví dụ thực tế

### Research về crypto project

```bash
fr --prompt "Research về Variational (ai-agent-trading), trình bày bằng tiếng Việt"
```

Output: `outputs/variational-report.md`

### Recipe cho ML model

```bash
fr --prompt "Give me recipe cho fine-tune Llama-3.1-8B trên dataset tiếng Việt, trình bày bằng tiếng Việt"
```

Output: `outputs/llama-3-1-8b-vietnamese-recipe.md`

## Troubleshooting

### Lỗi: "command not found: fr"
- Chạy: `source ~/.bashrc`
- Hoặc thêm vào shell profile hiện tại

### Lỗi: "Permission denied"
- Kiểm tra: `ls -la ~/.local/bin/feynman`
- Fix: `chmod +x ~/.local/bin/feynman`

### Lỗi: "Cannot find module"
- Feynman CLI bị hỏng, cài lại: `curl -fsSL https://feynman.is/install | bash`

## References

- MemPalace: `~/.hermes/mempalace/feynman-configuration.md`
- Feynman Docs: https://feynman.is/docs
- Workspace: `~/julius-workspace/personal/researchs/`

---

*Last updated: 2026-05-23*