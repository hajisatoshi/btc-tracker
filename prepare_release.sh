#!/bin/bash
"""
Production Release Preparation Script
Prepares the BTC Portfolio Tracker for GitHub release
"""

echo "🚀 BTC Portfolio Tracker - Production Release Setup"
echo "=================================================="

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Initialize git repository if not already done
if [ ! -d .git ]; then
    echo "📝 Initializing Git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Add all files to git
echo "📦 Adding files to Git..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "feat: Initial release of BTC Portfolio Tracker v2.0

- Multi-currency support (USD, CAD, EUR, GBP)
- Savings and spending tracking
- Real-time Bitcoin price monitoring
- User authentication and data security
- CSV import/export functionality
- Production-ready executable builds
- Comprehensive documentation"

# Create version tag
echo "🏷️  Creating version tag..."
git tag -a v2.0.0 -m "BTC Portfolio Tracker v2.0.0 - Production Release

Features:
- Complete multi-currency support
- Enhanced UI with tabbed interface
- Improved security and authentication
- Production build system
- Comprehensive documentation

This is the first production-ready release."

echo ""
echo "✅ Production setup completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Create a new repository on GitHub"
echo "2. Add remote origin: git remote add origin <your-repo-url>"
echo "3. Push to GitHub: git push -u origin main"
echo "4. Push tags: git push --tags"
echo "5. Create a release on GitHub using the v2.0.0 tag"
echo ""
echo "📁 Files ready for distribution:"
echo "- dist/BTC-Portfolio-Tracker (Linux executable)"
echo "- Complete source code with documentation"
echo "- Build scripts for other platforms"
echo ""
echo "🎉 Your BTC Portfolio Tracker is ready for release!"
