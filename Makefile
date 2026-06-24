.PHONY: test lint build clean

# 运行全部测试
test:
	cd p001-audio-separator/backend && python -m pytest -v
	cd p001-audio-separator/web && npx vitest run

# 代码检查
lint:
	cd p001-audio-separator/backend && ruff check .
	cd p001-audio-separator/backend && mypy app/
	cd p001-audio-separator/web && npx eslint src/
	cd p001-audio-separator/web && npx prettier --check src/

# 格式化
format:
	cd p001-audio-separator/backend && ruff format .
	cd p001-audio-separator/web && npx prettier --write src/

# 构建 Docker 镜像
build:
	cd p001-audio-separator && docker compose build

# 清理临时文件
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf p001-audio-separator/web/dist/
	rm -rf p001-audio-separator/backend/htmlcov/
