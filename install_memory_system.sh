#!/bin/bash

# Memory & Learning System - Installation Script
# This script installs the memory system into your project

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Memory & Learning System - Installer${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if package exists
if [ ! -f "memory_system_complete.tar.gz" ]; then
    echo -e "${RED}Error: memory_system_complete.tar.gz not found!${NC}"
    echo "Please download the package first."
    exit 1
fi

# Get project root (default: current directory)
PROJECT_ROOT="${1:-.}"

echo -e "${YELLOW}Installation directory: ${PROJECT_ROOT}${NC}\n"

# Confirm installation
read -p "Install memory system to ${PROJECT_ROOT}? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

# Create temporary directory
TEMP_DIR=$(mktemp -d)
echo -e "${BLUE}Extracting package...${NC}"
tar -xzf memory_system_complete.tar.gz -C "$TEMP_DIR"

# Check if directories exist, create if not
echo -e "${BLUE}Checking project structure...${NC}"

mkdir -p "${PROJECT_ROOT}/src"
mkdir -p "${PROJECT_ROOT}/config"
mkdir -p "${PROJECT_ROOT}/docs"
mkdir -p "${PROJECT_ROOT}/scripts"
mkdir -p "${PROJECT_ROOT}/data/memory"

# Copy files
echo -e "${BLUE}Installing files...${NC}"

echo "  → Copying memory module to src/"
cp -r "${TEMP_DIR}/memory_system/src/memory" "${PROJECT_ROOT}/src/"

echo "  → Copying configuration"
cp "${TEMP_DIR}/memory_system/config/memory.yaml" "${PROJECT_ROOT}/config/"

echo "  → Copying documentation"
cp "${TEMP_DIR}/memory_system/docs/MEMORY_SYSTEM_GUIDE.md" "${PROJECT_ROOT}/docs/"

echo "  → Copying demo script"
cp "${TEMP_DIR}/memory_system/scripts/demo_memory_system.py" "${PROJECT_ROOT}/scripts/"

echo "  → Copying reference documentation"
cp "${TEMP_DIR}/memory_system/MEMORY_INSTALLATION.md" "${PROJECT_ROOT}/"
cp "${TEMP_DIR}/memory_system/MEMORY_QUICK_REFERENCE.md" "${PROJECT_ROOT}/"
cp "${TEMP_DIR}/memory_system/MEMORY_SYSTEM_DELIVERY.md" "${PROJECT_ROOT}/"

# Update requirements.txt
echo "  → Updating requirements.txt"
if [ -f "${PROJECT_ROOT}/requirements.txt" ]; then
    # Check if chromadb already in requirements
    if ! grep -q "chromadb" "${PROJECT_ROOT}/requirements.txt"; then
        echo -e "\n# Memory & Learning System" >> "${PROJECT_ROOT}/requirements.txt"
        echo "chromadb>=0.4.0" >> "${PROJECT_ROOT}/requirements.txt"
        echo "sentence-transformers>=2.2.0" >> "${PROJECT_ROOT}/requirements.txt"
    else
        echo "    (chromadb already in requirements.txt)"
    fi
else
    # Create new requirements.txt
    cat "${TEMP_DIR}/memory_system/requirements.txt" > "${PROJECT_ROOT}/requirements.txt"
fi

# Cleanup
rm -rf "$TEMP_DIR"

echo -e "\n${GREEN}✓ Installation complete!${NC}\n"

# Summary
echo -e "${BLUE}Files installed:${NC}"
echo "  • src/memory/ (14 Python modules)"
echo "  • config/memory.yaml"
echo "  • docs/MEMORY_SYSTEM_GUIDE.md"
echo "  • scripts/demo_memory_system.py"
echo "  • MEMORY_INSTALLATION.md"
echo "  • MEMORY_QUICK_REFERENCE.md"
echo "  • MEMORY_SYSTEM_DELIVERY.md"
echo "  • requirements.txt (updated)"

echo -e "\n${YELLOW}Next steps:${NC}"
echo "  1. Install dependencies:"
echo "     ${BLUE}pip install chromadb sentence-transformers${NC}"
echo ""
echo "  2. Run demo to verify installation:"
echo "     ${BLUE}cd ${PROJECT_ROOT} && python scripts/demo_memory_system.py${NC}"
echo ""
echo "  3. Read the documentation:"
echo "     ${BLUE}cat ${PROJECT_ROOT}/MEMORY_INSTALLATION.md${NC}"
echo ""
echo "  4. Start integrating with your agents:"
echo "     ${BLUE}cat ${PROJECT_ROOT}/MEMORY_QUICK_REFERENCE.md${NC}"

echo -e "\n${GREEN}For detailed instructions, see: MEMORY_INSTALLATION.md${NC}\n"
