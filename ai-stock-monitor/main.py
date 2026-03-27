#!/usr/bin/env python3
"""
AI Stock Monitor - 股票盯盘交易分析系统
主入口文件
"""

import streamlit as st
from ui import create_app

def main():
    """主函数"""
    app = create_app()
    app.run(server_port=8501)

if __name__ == "__main__":
    main()
