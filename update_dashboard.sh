#!/bin/bash
# Quick update script - fetch data and regenerate dashboard

cd "$(dirname "$0")"

echo "🔄 Updating AI Penetration Dashboard..."
echo ""

# Fetch data
echo "1️⃣ Fetching data from Snowflake..."
../venv/bin/python fetch_data.py

if [ $? -ne 0 ]; then
    echo "❌ Data fetch failed"
    exit 1
fi

# Generate HTML
echo ""
echo "2️⃣ Generating dashboard HTML..."
../venv/bin/python generate_dashboard.py

if [ $? -ne 0 ]; then
    echo "❌ Dashboard generation failed"
    exit 1
fi

echo ""
echo "✅ Dashboard updated successfully!"
echo "📂 Open: ai_penetration_dashboard.html"
