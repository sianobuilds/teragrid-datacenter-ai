#!/bin/bash
echo "🚀 Auto-syncing TeraGrid-Ops to GitHub..."
git add .
MSG="feat: enhance visual 32-node thermal heatmap & async queue orchestrator - $(date '+%Y-%m-%d %H:%M:%S')"
git commit -m "$MSG"
git push origin main
echo "✅ Successfully synced to GitHub!"
