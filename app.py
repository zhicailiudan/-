# -*- coding: utf-8 -*-
"""
十日终焉·知识觉醒 — 沉浸式主界面
统一的场景流驱动体验，融合剧情/战斗/学习/势力/回响
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()

from core.knowledge_base import KnowledgeBaseManager
from core.rag_engine import RAGEngine
from agents.role_manager import AgentRole, get_role_info, get_all_roles
from story.story_engine import StoryEngine
from story.game_save import NewGame, GameSave
from story.battle_integrator import BattleIntegrator
from story.faction_manager import FactionManager
from story.reverberation_system import ReverberationSystem
from story.constants import FACTION_NAMES
from story.main_story import STORY_DATA
from story.dungeon_generator import DungeonGenerator, DungeonManifest
from story.ui_particles import init_particle_system
from story.ui_physics import init_physics_system
from storage.session_manager import load_state, save_state, get_messages, add_message, save_messages

# ===== 页面配置 =====
st.set_page_config(page_title="十日终焉·知识觉醒", page_icon="⌛", layout="wide", initial_sidebar_state="expanded")

# ===== 全局 CSS 注入 =====
def inject_css():
    st.markdown("""
<style>
    /* ===== 隐藏 Streamlit 原生元素 ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display: none;}
    div[data-testid="stToolbar"] {display: none;}
    div[data-testid="stDecoration"] {display: none;}

    /* ===== 全局背景 ===== */
    .stApp {
        background:
            radial-gradient(ellipse 70% 50% at 15% 20%, rgba(196,146,72,0.08), transparent 60%),
            radial-gradient(ellipse 60% 50% at 85% 80%, rgba(139,92,246,0.07), transparent 55%),
            radial-gradient(ellipse 50% 40% at 50% 50%, rgba(185,28,28,0.03), transparent 50%),
            linear-gradient(170deg, #070A0F 0%, #0B0F18 40%, #090C15 70%, #080B14 100%) !important;
        color: #F2F0E8;
    }
    .stApp::before {
        content: '';
        position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");
        pointer-events: none; z-index: 0;
    }
    .main > div {padding: 0 !important; position: relative; z-index: 1;}

    /* ===== 主容器 ===== */
    .block-container {
        max-width: 1360px !important;
        padding: 2rem 3rem 10rem !important;
    }

    /* ===== 滚动条 ===== */
    ::-webkit-scrollbar {width: 5px;}
    ::-webkit-scrollbar-track {background: #070A0F;}
    ::-webkit-scrollbar-thumb {background: rgba(196,146,72,0.25); border-radius: 999px;}
    ::-webkit-scrollbar-thumb:hover {background: rgba(196,146,72,0.45);}

    /* ===== 标题区 ===== */
    .end-title {
        font-family: 'Noto Serif SC', 'SimSun', 'Songti SC', serif;
        font-size: 2.4rem; font-weight: 900;
        color: #C49248; letter-spacing: 0.12em;
        text-shadow: 0 0 40px rgba(196,146,72,0.15), 0 2px 0 rgba(0,0,0,0.3);
        position: relative; display: inline-block;
    }
    .end-title .sep {
        color: rgba(196,146,72,0.4); margin: 0 0.15em;
        font-weight: 300;
    }
    .title-row {
        display: flex; align-items: baseline; gap: 1.2rem;
        margin-bottom: 0.2rem; flex-wrap: wrap;
    }
    .title-english {
        font-family: 'Courier New', monospace;
        font-size: 0.7rem; color: rgba(196,146,72,0.35);
        letter-spacing: 0.3em; text-transform: uppercase;
        margin-top: 0.4rem;
    }
    .end-subtitle {
        font-size: 0.9rem; color: #AFA89C;
        letter-spacing: 0.08em; margin: 0.1rem 0 0.5rem;
        font-style: italic; opacity: 0.7;
        border-left: 2px solid rgba(196,146,72,0.2);
        padding-left: 1rem;
    }
    .end-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, rgba(196,146,72,0.18) 20%, rgba(196,146,72,0.18) 80%, transparent 100%);
        margin: 0.6rem 0 1.2rem; border: none;
    }

    /* ===== 轮回档案状态栏 ===== */
    .archive-grid {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 10px; margin: 0 0 1.2rem;
    }
    @media (max-width: 900px) {
        .archive-grid {grid-template-columns: repeat(3, 1fr);}
    }
    @media (max-width: 520px) {
        .archive-grid {grid-template-columns: repeat(2, 1fr);}
    }
    .status-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(196,146,72,0.18);
        border-radius: 12px; padding: 14px 16px;
        transition: border-color 0.2s, background 0.2s;
        cursor: default;
    }
    .status-card:hover {
        border-color: rgba(196,146,72,0.35);
        background: rgba(255,255,255,0.06);
    }
    .status-card .label {
        font-size: 0.65rem; color: #8E879A;
        letter-spacing: 0.18em; text-transform: uppercase;
        margin-bottom: 6px; font-family: 'Courier New', monospace;
    }
    .status-card .value {
        font-size: 1.35rem; font-weight: 800;
        line-height: 1.2; letter-spacing: 0.02em;
    }

    /* ===== 模块标题 ===== */
    .section-title {
        font-size: 1rem; font-weight: 700; color: #C49248;
        letter-spacing: 0.08em; margin: 1.6rem 0 0.8rem;
        display: flex; align-items: center; gap: 0.6rem;
    }
    .section-title .en {
        font-size: 0.6rem; color: rgba(196,146,72,0.35);
        font-weight: 400; letter-spacing: 0.2em;
        font-family: 'Courier New', monospace;
    }
    .section-title::after {
        content: ''; flex: 1; height: 1px;
        background: linear-gradient(90deg, rgba(196,146,72,0.15), transparent);
    }

    /* ===== 通用卡片 ===== */
    .trial-card {
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(196,146,72,0.18);
        border-radius: 16px; padding: 20px 24px;
        box-shadow: 0 12px 40px rgba(0,0,0,0.25);
    }

    /* ===== 角色档案卡 ===== */
    .role-card {
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(196,146,72,0.18);
        border-radius: 16px; padding: 20px 24px;
        box-shadow: 0 12px 40px rgba(0,0,0,0.25);
        height: 100%;
    }
    .role-card .badge {
        font-size: 0.65rem; color: #8E879A;
        letter-spacing: 0.14em; font-family: 'Courier New', monospace;
        margin-bottom: 8px;
    }
    .role-card .name {
        font-size: 1.25rem; font-weight: 800; color: #C49248;
        letter-spacing: 0.04em;
    }
    .role-card .title {
        font-size: 0.85rem; color: #A78BFA; margin: 4px 0 10px;
        letter-spacing: 0.04em;
    }
    .role-card .desc {
        font-size: 0.9rem; line-height: 1.7; color: #C9C3B7;
    }

    /* ===== Selectbox 美化 ===== */
    div[data-baseweb="select"] {
        margin-bottom: 0;
    }
    div[data-baseweb="select"] > div {
        background-color: #111722 !important;
        border: 1px solid rgba(196,146,72,0.28) !important;
        border-radius: 10px !important;
        min-height: 48px !important;
        box-shadow: none !important;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: rgba(196,146,72,0.45) !important;
    }
    div[data-baseweb="select"] > div:focus-within {
        border-color: #C49248 !important;
        box-shadow: 0 0 0 2px rgba(196,146,72,0.15) !important;
    }
    div[data-baseweb="select"] * {
        color: #F2F0E8 !important;
    }
    div[data-baseweb="select"] span {
        color: #F2F0E8 !important;
    }
    div[data-baseweb="select"] svg {
        fill: rgba(196,146,72,0.5) !important;
    }
    /* dropdown menu */
    div[data-baseweb="popover"] div[data-baseweb="menu"] {
        background: #111722 !important;
        border: 1px solid rgba(196,146,72,0.2) !important;
        border-radius: 10px !important;
    }
    div[role="option"] {
        color: #C9C3B7 !important;
        font-size: 0.9rem !important;
    }
    div[role="option"]:hover {
        background: rgba(196,146,72,0.1) !important;
    }

    /* ===== st.chat_message 聊天气泡 ===== */
    div[data-testid="stChatMessage"] {
        background: rgba(17,24,39,0.78) !important;
        border: 1px solid rgba(196,146,72,0.12) !important;
        border-radius: 14px !important;
        padding: 14px 18px !important;
        margin-bottom: 14px !important;
        animation: msg-fadein 0.25s ease-out;
    }
    @keyframes msg-fadein {
        from {opacity: 0; transform: translateY(6px);}
        to {opacity: 1; transform: translateY(0);}
    }
    /* 用户消息气泡 */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
        background: rgba(196,146,72,0.10) !important;
        border-color: rgba(196,146,72,0.22) !important;
    }
    /* AI 消息气泡 */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
        background: rgba(17,24,39,0.85) !important;
        border-color: rgba(139,92,246,0.20) !important;
    }
    /* 消息文字 */
    div[data-testid="stChatMessage"] p {
        font-size: 0.95rem !important;
        line-height: 1.75 !important;
        color: #D8D3CA !important;
    }
    div[data-testid="stChatMessage"] strong {
        font-size: 0.8rem !important;
        color: #A78BFA !important;
        letter-spacing: 0.06em;
    }
    /* 头像 */
    div[data-testid="chatAvatarIcon-user"],
    div[data-testid="chatAvatarIcon-assistant"] {
        font-size: 0.8rem !important;
    }

    /* ===== 空聊天提示 ===== */
    .chat-empty {
        text-align: center; padding: 3rem 1rem;
        color: #8E879A; font-size: 0.9rem;
        border: 1px dashed rgba(196,146,72,0.12);
        border-radius: 16px; margin: 0.6rem 0 1rem;
        line-height: 1.7;
    }

    /* ===== st.chat_input 底部输入区美化 ===== */
    div[data-testid="stChatInput"] {
        background: rgba(9,13,22,0.85) !important;
        border: none !important;
        border-top: 1px solid rgba(196,146,72,0.1) !important;
        padding: 0.8rem 1rem !important;
    }
    div[data-testid="stChatInput"] > div {
        max-width: 1360px !important; margin: 0 auto !important;
    }
    div[data-testid="stChatInput"] textarea {
        background: #111722 !important;
        color: #F2F0E8 !important;
        border: 1px solid rgba(196,146,72,0.22) !important;
        border-radius: 12px !important;
        font-size: 0.9rem !important;
        padding: 0.75rem 1rem !important;
        caret-color: #C49248 !important;
    }
    div[data-testid="stChatInput"] textarea:focus {
        border-color: #C49248 !important;
        box-shadow: 0 0 0 2px rgba(196,146,72,0.1) !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #6B6478 !important; font-style: italic;
    }
    div[data-testid="stChatInput"] button {
        background: linear-gradient(135deg, rgba(196,146,72,0.2), rgba(196,146,72,0.35)) !important;
        border: 1px solid rgba(196,146,72,0.3) !important;
        border-radius: 10px !important;
        color: #C49248 !important;
        font-size: 1.1rem !important;
        transition: all 0.2s !important;
    }
    div[data-testid="stChatInput"] button:hover {
        background: linear-gradient(135deg, rgba(196,146,72,0.3), rgba(196,146,72,0.5)) !important;
        border-color: rgba(196,146,72,0.5) !important;
    }

    /* ===== 场景容器 ===== */
    .scene-container {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(196,146,72,0.18);
        border-radius: 16px; padding: 28px 32px; margin: 12px 0;
        position: relative; overflow: hidden;
    }
    .scene-container::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent, rgba(196,146,72,0.3), transparent);
    }
    .scene-title {
        font-family: 'Noto Serif SC', 'SimSun', serif;
        font-size: 1.15rem; font-weight: 700;
        color: #C49248; text-align: center;
        padding-bottom: 10px; margin-bottom: 14px;
        border-bottom: 1px solid rgba(196,146,72,0.1);
        letter-spacing: 0.08em;
    }
    .scene-text {
        font-size: 1rem; line-height: 2; color: #C9C3B7;
        text-indent: 2em; margin-bottom: 20px;
    }

    /* ===== NPC 对话框 ===== */
    .npc-box {
        background: linear-gradient(135deg, rgba(17,18,31,0.8), rgba(10,10,21,0.8));
        border-left: 3px solid rgba(185,28,28,0.6);
        padding: 18px 22px; margin: 16px 0;
        border-radius: 0 12px 12px 0;
    }
    .npc-box .name {
        font-size: 0.85rem; color: rgba(239,68,68,0.9);
        font-weight: 700; margin-bottom: 8px; letter-spacing: 0.12em;
    }
    .npc-box .line {
        font-size: 1rem; line-height: 1.9; color: #C9C3B7;
        font-style: italic;
    }
    .npc-box .line::before {content: '「'; color: rgba(239,68,68,0.6);}
    .npc-box .line::after {content: '」'; color: rgba(239,68,68,0.6);}

    /* ===== 道城卡片 ===== */
    .hub-grid {display: flex; gap: 14px; flex-wrap: wrap; margin: 14px 0;}
    .hub-card {
        flex: 1; min-width: 150px;
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(196,146,72,0.16);
        border-radius: 14px; padding: 20px 16px; text-align: center;
        cursor: pointer; transition: all 0.25s ease;
    }
    .hub-card:hover {
        border-color: rgba(196,146,72,0.4);
        transform: translateY(-3px);
        box-shadow: 0 10px 35px rgba(0,0,0,0.35);
        background: rgba(255,255,255,0.07);
    }
    .hub-card .icon {font-size: 1.8rem; margin-bottom: 8px;}
    .hub-card .name {font-size: 0.9rem; color: #E8E3D8; letter-spacing: 0.06em;}
    .hub-card .desc {font-size: 0.7rem; color: #8E879A; margin-top: 4px;}
    .hub-card .overlay {
        border-color: rgba(139,92,246,0.3);
        background: rgba(255,255,255,0.055);
    }

    /* ===== 战斗区域 ===== */
    .battle-header {
        text-align: center; padding: 20px; margin-bottom: 14px;
        border-bottom: 1px solid rgba(185,28,28,0.15);
    }
    .battle-zodiac {
        font-size: 1.4rem; color: rgba(239,68,68,0.9);
        font-weight: 800; letter-spacing: 0.16em;
        text-shadow: 0 0 30px rgba(239,68,68,0.15);
    }
    .battle-level-tag {
        display: inline-block; padding: 3px 14px; border-radius: 20px;
        font-size: 0.7rem; letter-spacing: 0.1em; margin: 4px 0;
    }
    .battle-level-tag.human {background: rgba(34,197,94,0.1); color: #22C55E; border: 1px solid rgba(34,197,94,0.3);}
    .battle-level-tag.earth {background: rgba(251,191,36,0.1); color: #FBBF24; border: 1px solid rgba(251,191,36,0.3);}
    .battle-level-tag.heaven {background: rgba(239,68,68,0.1); color: #EF4444; border: 1px solid rgba(239,68,68,0.3);}
    .battle-result-box {
        text-align: center; padding: 40px; border-radius: 16px; margin: 20px 0;
    }
    .battle-result-box.win {
        background: linear-gradient(135deg,rgba(0,200,0,0.06),rgba(0,150,0,0.04));
        border: 1px solid rgba(34,197,94,0.3);
    }
    .battle-result-box.lose {
        background: linear-gradient(135deg,rgba(200,0,0,0.06),rgba(150,0,0,0.04));
        border: 1px solid rgba(239,68,68,0.3);
    }
    .battle-result-box .result-icon {font-size: 2.5rem; margin-bottom: 10px;}
    .battle-result-box .result-text {font-size: 1rem; color: #C9C3B7;}
    .battle-result-box .dao-reward {color: #FACC15; font-size: 1.1rem; margin-top: 10px;}
    .battle-result-box .exp-reward {color: #C49248; font-size: 0.95rem;}

    /* ===== 题目框 ===== */
    .q-container {
        background: rgba(10,10,18,0.8); border: 1px solid rgba(196,146,72,0.12);
        border-radius: 14px; padding: 24px; margin: 16px 0;
    }
    .q-text {
        font-size: 1.05rem; color: #E8E3D8; line-height: 1.8;
        margin-bottom: 20px; padding-bottom: 16px;
        border-bottom: 1px solid rgba(196,146,72,0.08);
    }
    .q-progress {
        display: flex; justify-content: space-between;
        font-size: 0.75rem; color: #8E879A; margin-top: 12px;
    }

    /* ===== 通知 ===== */
    .notification {
        position: fixed; top: 30px; left: 50%; transform: translateX(-50%);
        background: rgba(17,18,30,0.95);
        border: 1px solid rgba(196,146,72,0.35);
        border-radius: 12px; padding: 14px 28px; z-index: 99999;
        animation: notify-in 0.35s ease, notify-out 0.35s ease 2.8s forwards;
        box-shadow: 0 0 50px rgba(196,146,72,0.12);
        backdrop-filter: blur(12px);
    }
    @keyframes notify-in {
        from {opacity: 0; transform: translateX(-50%) translateY(-16px);}
        to {opacity: 1; transform: translateX(-50%) translateY(0);}
    }
    @keyframes notify-out {
        from {opacity: 1;} to {opacity: 0; transform: translateX(-50%) translateY(-12px);}
    }

    /* ===== 日过渡 ===== */
    .day-transition {
        text-align: center; padding: 60px 20px;
        min-height: 50vh; display: flex; flex-direction: column;
        justify-content: center; align-items: center;
    }
    .day-transition .day-number {
        font-size: 3.5rem; font-weight: 900; color: #A78BFA;
        text-shadow: 0 0 50px rgba(167,139,250,0.25);
        animation: day-pulse 2s ease-in-out;
    }
    @keyframes day-pulse {
        0% {opacity: 0; transform: scale(0.5); text-shadow: 0 0 0 transparent;}
        30% {opacity: 1; transform: scale(1.08); text-shadow: 0 0 60px rgba(167,139,250,0.4);}
        60% {transform: scale(1);}
        100% {opacity: 1;}
    }
    .day-transition .day-title {
        font-size: 1.3rem; color: #C49248; letter-spacing: 0.15em;
        margin-top: 12px; animation: day-fade 1.5s ease-in-out;
    }
    .day-transition .day-quote {
        color: #8E879A; font-size: 0.8rem; margin-top: 24px;
        font-style: italic; animation: day-fade 2s ease-in-out;
        max-width: 380px; line-height: 1.8;
    }
    @keyframes day-fade {
        0% {opacity: 0; transform: translateY(10px);}
        60% {opacity: 0;}
        100% {opacity: 1; transform: translateY(0);}
    }

    /* ===== 回响觉醒 overlay ===== */
    .rev-awakening {
        position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
        background: radial-gradient(ellipse at center, rgba(10,10,46,0.97), rgba(0,0,0,0.98));
        border: 1px solid rgba(139,92,246,0.4);
        border-radius: 20px; padding: 40px 60px; z-index: 99999; text-align: center;
        animation: rev-appear 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        box-shadow: 0 0 60px rgba(139,92,246,0.15);
    }
    @keyframes rev-appear {
        0% {opacity: 0; transform: translate(-50%, -50%) scale(0.3);}
        60% {transform: translate(-50%, -50%) scale(1.03);}
        100% {opacity: 1; transform: translate(-50%, -50%) scale(1);}
    }
    .rev-awakening .rev-icon {font-size: 2.5rem; margin-bottom: 8px;}
    .rev-awakening .rev-title {font-size: 1.2rem; color: #A78BFA; letter-spacing: 0.15em; text-shadow: 0 0 20px rgba(167,139,250,0.3);}
    .rev-awakening .rev-name {font-size: 1.5rem; color: #F2F0E8; margin: 8px 0;}
    .rev-awakening .rev-desc {font-size: 0.85rem; color: #8E879A; margin-top: 8px;}

    /* ===== 回响卡片 ===== */
    .rev-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(139,92,246,0.15);
        border-radius: 12px; padding: 16px; margin: 10px 0;
    }
    .rev-card.active {
        border-color: rgba(139,92,246,0.35);
        box-shadow: 0 0 20px rgba(139,92,246,0.08);
    }
    .rev-card .rname {color: #E8E3D8; font-weight: 700; font-size: 0.95rem;}
    .rev-card .rlevel {
        display: inline-block; padding: 2px 10px; border-radius: 10px;
        background: rgba(139,92,246,0.12); color: #A78BFA; font-size: 0.7rem;
    }
    .rev-card .rdesc {color: #C9C3B7; font-size: 0.8rem; margin-top: 6px;}
    .rev-card .reffects {color: #8E879A; font-size: 0.75rem; margin-top: 4px;}

    /* ===== 按钮统一样式 ===== */
    .stButton > button {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(196,146,72,0.25) !important;
        color: #D8D3CA !important;
        border-radius: 10px !important;
        padding: 0.55rem 1.2rem !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        width: 100%;
        letter-spacing: 0.04em;
    }
    .stButton > button:hover {
        border-color: rgba(196,146,72,0.45) !important;
        background: rgba(255,255,255,0.09) !important;
        box-shadow: 0 0 25px rgba(196,146,72,0.08) !important;
        transform: none !important;
    }
    .stButton > button:active {
        transform: translateY(1px) !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, rgba(196,146,72,0.2), rgba(196,146,72,0.35)) !important;
        border-color: rgba(196,146,72,0.35) !important;
        color: #E8DCC8 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, rgba(196,146,72,0.3), rgba(196,146,72,0.45)) !important;
        border-color: rgba(196,146,72,0.5) !important;
    }

    /* ===== 侧边栏 ===== */
    section[data-testid="stSidebar"] {
        background: #080B14 !important;
        border-right: 1px solid rgba(196,146,72,0.08);
    }
    section[data-testid="stSidebar"] .stMarkdown {color: #C9C3B7;}
    .sidebar-title {
        font-size: 1rem; color: #C49248;
        letter-spacing: 0.12em; margin-bottom: 4px;
        font-weight: 700;
    }
    .sidebar-divider {
        height: 1px; background: rgba(196,146,72,0.1);
        border: none; margin: 14px 0;
    }

    /* ===== 势力管理 ===== */
    .faction-card {
        background: rgba(255,255,255,0.045);
        border-radius: 12px; padding: 18px; margin: 10px 0;
    }
    .faction-card .fname {
        font-size: 1rem; color: #C49248; font-weight: 700;
    }
    .faction-card .fdesc {
        font-size: 0.8rem; color: #8E879A; margin: 6px 0;
    }

    /* ===== 知识引子框 ===== */
    .knowledge-seed {
        padding: 14px 18px;
        border-left: 3px solid rgba(196,146,72,0.4);
        background: rgba(196,146,72,0.04);
        border-radius: 0 10px 10px 0;
        margin: 12px 0;
    }
    .knowledge-seed .seed-text {
        font-size: 0.9rem; color: #C9C3B7;
        font-style: italic; line-height: 1.7;
    }

    /* ===== 着陆页标题特大版 ===== */
    .landing-title {
        font-family: 'Noto Serif SC', 'SimSun', serif;
        font-size: 3.2rem; font-weight: 900;
        color: #C49248; letter-spacing: 0.15em;
        text-shadow: 0 0 60px rgba(196,146,72,0.12), 0 2px 0 rgba(0,0,0,0.3);
    }
    .landing-warning {
        font-size: 0.75rem; color: rgba(239,68,68,0.6);
        letter-spacing: 0.2em; font-family: 'Courier New', monospace;
    }
</style>
""", unsafe_allow_html=True)

# ===== 初始化粒子 & 物理系统 =====
init_particle_system()
init_physics_system()

# ===== 会话状态初始化 =====
def init_session():
    """初始化所有会话状态"""
    if "initialized" in st.session_state:
        return

    # 核心系统
    st.session_state.kb_manager = KnowledgeBaseManager()
    saved_state = load_state()

    # 知识库
    saved_kb_id = saved_state.get("current_kb_id") if saved_state else None
    if saved_kb_id and st.session_state.kb_manager.get_kb(saved_kb_id):
        kb_id = saved_kb_id
    else:
        kbs = list(st.session_state.kb_manager.kbs.keys())
        kb_id = kbs[0] if kbs else st.session_state.kb_manager.create_kb("默认知识库", "学习基础知识")
    st.session_state.kb_id = kb_id

    # 角色
    saved_role = saved_state.get("current_role", "qixia") if saved_state else "qixia"
    st.session_state.role = saved_role

    # 游戏状态
    st.session_state.game_phase = "LANDING"
    st.session_state.engine = None
    st.session_state.battle_integrator = None
    st.session_state.last_scene_id = None
    st.session_state.notification = None
    st.session_state.day_transition = None
    st.session_state.last_rev_count = 0
    st.session_state.new_rev_notification = None

    # RAG
    st.session_state.rag_engine = None

    # 对话记录
    st.session_state.messages = {}

    # 存档
    st.session_state.save_manager = GameSave()

    # 副本系统
    st.session_state.dungeon_generator = None
    st.session_state.dungeon_manifest = None
    st.session_state.dungeon_loaded_kb_text = ""
    st.session_state.dungeon_selected_char = "qixia"
    st.session_state.dungeon_initial_shown = False
    st.session_state.dungeon_chat_history = []
    st.session_state.dungeon_reward_given = False

    st.session_state.initialized = True

def get_engine() -> StoryEngine:
    """获取或创建 StoryEngine"""
    if st.session_state.engine is None:
        engine = NewGame.create_initial_state()
        engine.load_story(STORY_DATA)
        st.session_state.engine = engine
    return st.session_state.engine

def get_rag_engine():
    """获取或创建 RAGEngine"""
    if st.session_state.rag_engine is None:
        try:
            role_enum = AgentRole(st.session_state.role)
        except ValueError:
            role_enum = AgentRole.QIXIA
        st.session_state.rag_engine = RAGEngine(
            st.session_state.kb_id, role_enum
        )
    return st.session_state.rag_engine

def switch_rag_role(role: str):
    """切换 RAG 角色"""
    st.session_state.role = role
    try:
        role_enum = AgentRole(role)
    except ValueError:
        role_enum = AgentRole.QIXIA
    rag = get_rag_engine()
    if rag:
        rag.switch_role(role_enum)
    save_state({"current_role": role, "current_kb_id": st.session_state.kb_id})

def start_game():
    """开始新游戏"""
    engine = get_engine()
    engine.start_day(1)
    st.session_state.game_phase = "STORY"
    st.session_state.last_rev_count = len([r for r in engine.state.player.reverberations if "_lv" in r])

def set_phase(phase: str):
    """切换游戏阶段"""
    st.session_state.game_phase = phase
    if phase != "STORY":
        st.session_state.last_scene_id = None

def auto_save():
    """在关键节点自动存档"""
    if st.session_state.engine:
        st.session_state.save_manager.quick_save(st.session_state.engine)

def show_notification(text: str):
    """发送通知"""
    st.session_state.notification = text

# ===== 侧边栏 =====
def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-title">☰ 终焉面板</div>', unsafe_allow_html=True)
        st.markdown('<div class="end-divider"></div>', unsafe_allow_html=True)

        # 存档管理
        st.markdown("**💾 存档**")
        saves = st.session_state.save_manager.list_saves()
        if saves:
            save_names = [s["name"] for s in saves[:5]]
            for sname in save_names:
                if st.button(f"📂 {sname[:16]}", key=f"load_{sname}", use_container_width=True):
                    loaded = st.session_state.save_manager.load(sname)
                    if loaded:
                        loaded.load_story(STORY_DATA)
                        st.session_state.engine = loaded
                        if loaded.current_scene:
                            st.session_state.game_phase = "STORY"
                        else:
                            st.session_state.game_phase = "EXPLORATION"
                        st.rerun()

        if st.button("💾 快速存档", use_container_width=True):
            if st.session_state.engine:
                st.session_state.save_manager.quick_save(st.session_state.engine)
                st.success("已存档")
                st.rerun()

# ===== 状态栏 =====
def render_status_bar():
    engine = st.session_state.engine
    if not engine:
        return

    state = engine.state
    p = state.player
    prog = state.progression
    faction_name = FACTION_NAMES.get(p.faction, "无")
    rev_count = len([r for r in p.reverberations if "_lv" in r])
    day_str = f"第{prog.current_day}日"

    status_items = [
        ("轮回日", day_str, "#A78BFA"),
        ("道", str(p.dao), "#FACC15"),
        ("经验", str(p.exp), "#22D3EE"),
        ("势力", faction_name, "#EF4444"),
        ("回响", str(rev_count), "#60A5FA"),
        ("轮回", str(prog.cycle_count + 1), "#C49248"),
    ]

    st.markdown("""
    <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.3rem;">
        <div style="font-size:0.7rem; color:#8E879A; letter-spacing:0.16em; font-family:'Courier New',monospace;">轮回档案</div>
        <div style="font-size:0.6rem; color:rgba(196,146,72,0.25); font-family:'Courier New',monospace; letter-spacing:0.2em;">REINCARNATION ARCHIVE</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="archive-grid">', unsafe_allow_html=True)
    for label, value, color in status_items:
        st.markdown(f"""
        <div class="status-card">
            <div class="label">{label}</div>
            <div class="value" style="color:{color};">{value}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ===== 开场画面 =====
def render_landing():
    st.markdown("""
    <div class="day-transition" style="min-height:80vh;">
        <div class="landing-warning">⚠ 警 告 ： 进 入 后 将 无 法 回 头 ⚠</div>
        <div style="height:30px;"></div>
        <div class="landing-title">十日终焉 · 知识觉醒</div>
        <div style="font-family:'Courier New',monospace; font-size:0.6rem; color:rgba(196,146,72,0.3); letter-spacing:0.3em; margin-top:12px;">
            REINCARNATION TRIAL SYSTEM · KNOWLEDGE AWAKENING
        </div>
        <div style="width:120px; height:1px; background:linear-gradient(90deg,transparent,rgba(196,146,72,0.3),transparent); margin:24px auto;"></div>
        <div style="color:#AFA89C; font-size:0.85rem; letter-spacing:0.06em; text-align:center; max-width:420px; line-height:1.9; margin-bottom:30px;">
            在这里，知识就是力量。<br>
            通过十二生肖的试炼，收集「道」，觉醒你的回响。<br>
            十日后，要么逃离，要么沉沦。
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 检查是否有存档
    has_saves = len(st.session_state.save_manager.list_saves()) > 0

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔥 进 入 终 焉 之 地 🔥", use_container_width=True):
            start_game()
            st.rerun()

    if has_saves:
        st.markdown('<div style="text-align:center; margin-top:10px;">', unsafe_allow_html=True)
        if st.button("📂 继续上次的旅程", use_container_width=True):
            saves = st.session_state.save_manager.list_saves()
            if saves:
                loaded = st.session_state.save_manager.load(saves[0]["name"])
                if loaded:
                    loaded.load_story(STORY_DATA)
                    st.session_state.engine = loaded
                    set_phase("STORY" if loaded.current_scene else "EXPLORATION")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="text-align:center; color:#444; font-size:0.7rem; margin-top:20px;">v2.0 · 觉醒系统</div>', unsafe_allow_html=True)

# ===== 剧情场景 =====
def render_story():
    engine = st.session_state.engine
    if not engine or not engine.current_scene:
        st.info("尚未开始游戏，请先进入终焉之地")
        return

    # ===== 知识库切换（嵌入剧情） =====
    with st.expander("📚 知识库管理", expanded=False):
        kb_manager = st.session_state.kb_manager
        kbs = kb_manager.kbs
        kb_id = st.session_state.kb_id

        col_kb, col_stat = st.columns([2, 1])
        with col_kb:
            if kbs:
                kb_options = {k: v.name for k, v in kbs.items()}
                selected = st.selectbox(
                    "切换知识库", list(kb_options.keys()),
                    index=list(kb_options.keys()).index(kb_id) if kb_id in kb_options else 0,
                    format_func=lambda x: kb_options[x],
                    label_visibility="collapsed",
                    key="story_kb_selector"
                )
                if selected != kb_id:
                    st.session_state.kb_id = selected
                    st.session_state.rag_engine = None
                    st.rerun()
        with col_stat:
            kb_obj = kb_manager.get_kb(st.session_state.kb_id)
            if kb_obj:
                st.caption(f"📖 {kb_obj.name}")
                st.caption(f"🎯 {kb_obj.goal}")

        # 文档上传
        uploaded = st.file_uploader(
            "上传文档到当前知识库", type=["pdf", "txt", "md", "docx", "pptx"],
            key="story_file_upload"
        )
        if uploaded:
            from core.document_parser import DocumentParser
            from core.chunking import TextChunker
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded.name.split('.')[-1]}") as tmp:
                tmp.write(uploaded.getvalue())
                tmp_path = tmp.name
            try:
                text = DocumentParser.parse(tmp_path)
                chunker = TextChunker()
                chunks = chunker.chunk(text)
                rag = get_rag_engine()
                if rag:
                    rag.add_documents(chunks, doc_name=uploaded.name)
                kb_manager.add_document(st.session_state.kb_id, uploaded.name)
                st.success(f"✅ 已加载 {len(chunks)} 个知识块")
            except Exception as e:
                st.error(f"❌ 解析失败: {e}")
            finally:
                os.unlink(tmp_path)

    scene = engine.current_scene
    scene_id = scene.scene_id

    # 检查战斗触发
    if engine.state.progression.story_flags.get("in_battle"):
        zodiac = engine.state.progression.story_flags.get("current_battle", "rat")
        level = engine.state.progression.story_flags.get("current_level", "human")
        _init_battle(zodiac, level)
        set_phase("BATTLE")
        st.rerun()
        return

    # 检查自动推进
    if scene.auto_advance and scene.next_scene:
        engine.go_to_scene(scene.next_scene)
        st.rerun()
        return

    # 场景标题
    st.markdown(f"""
    <div class="section-title">
        ◈ {scene.title} ◈
        <span class="en">STORY</span>
    </div>
    """, unsafe_allow_html=True)

    # NPC 对话 vs 普通叙述
    if scene.npcs:
        npc_name = scene.npcs[0]
        npc_display = {
            "面试官": "面试官", "chutianqiu": "楚天秋", "jojiajin": "乔家劲",
            "yanchunchun": "燕知春", "qianmeck": "钱 Meck", "chennan": "陈俊南",
        }.get(npc_name, npc_name)
        st.markdown(f'<div class="npc-box"><div class="name">【{npc_display}】</div><div class="line">{scene.text}</div></div>', unsafe_allow_html=True)
    else:
        paragraphs = scene.text.split("\n\n")
        html = '<div class="scene-text">'
        for p in paragraphs:
            if p.strip():
                html += f"<p>{p.strip()}</p>"
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    # 选项
    choices = engine.get_available_choices()
    if choices:
        st.markdown("---")
        for c in choices:
            if st.button(f"▸ {c.text}", key=f"choice_{c.choice_id}", use_container_width=True):
                engine.make_choice(c.choice_id)
                # 保存状态
                save_state({
                    "current_role": st.session_state.role,
                    "current_kb_id": st.session_state.kb_id
                })

                # 检查是否进入新场景
                new_scene = engine.current_scene
                if new_scene and new_scene.scene_id == scene_id:
                    # 场景没变，说明可能是 day end
                    if not new_scene.choices and not new_scene.auto_advance:
                        set_phase("EXPLORATION")
                st.rerun()
    else:
        # 无选项 → day end / auto advance
        if scene.next_scene:
            engine.go_to_scene(scene.next_scene)
            st.rerun()
        else:
            st.markdown("---")
            st.markdown('<div style="text-align:center; padding:20px;">', unsafe_allow_html=True)
            if st.button("📖 进入自由探索", use_container_width=True):
                set_phase("EXPLORATION")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# ===== 道城探索 =====
def render_exploration():
    engine = st.session_state.engine
    if not engine:
        return
    state = engine.state
    day = state.progression.current_day
    day_titles = ["", "降临", "初试", "裂痕", "分岔", "攻城", "暗流", "背叛", "天位", "抉择", "终焉"]
    day_title = day_titles[day] if day < len(day_titles) else "终焉"

    st.markdown(f"""
    <div class="section-title" style="margin-top:0;">
        🏛 道城 · 第{day}日
        <span class="en">{day_title}</span>
    </div>
    <div style="color:#8E879A; font-size:0.8rem; margin-bottom:1rem; border-left:2px solid rgba(196,146,72,0.12); padding-left:12px;">
        在下次日出前，你可以自由行动
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="hub-grid">', unsafe_allow_html=True)

    # 使用列模拟网格
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="hub-card day-progress">
            <div class="icon">📖</div>
            <div class="name">继续剧情</div>
            <div class="desc">推进主线故事</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📖 继续剧情", key="hub_story", use_container_width=True):
            if day < 10:
                next_day_num = day + 1
                day_titles_map = {1:"降临",2:"初试",3:"裂痕",4:"分岔",5:"攻城",6:"暗流",7:"背叛",8:"天位",9:"抉择",10:"终焉"}
                st.session_state.day_transition = {
                    "day": next_day_num,
                    "title": day_titles_map.get(next_day_num, "终焉")
                }
                set_phase("DAY_TRANSITION")
            else:
                st.info("最终之日已至！")
            st.rerun()

    with col2:
        st.markdown("""
        <div class="hub-card">
            <div class="icon">⚔</div>
            <div class="name">挑战生肖</div>
            <div class="desc">通过答题获取道</div>
        </div>
        """, unsafe_allow_html=True)
        # 生肖选择器
        zodiac_opts = {
            "rat":"鼠·智慧","ox":"牛·力量","tiger":"虎·威猛","rabbit":"兔·敏捷",
            "dragon":"龙·全面","snake":"蛇·阴柔","horse":"马·速度","sheep":"羊·温顺",
            "monkey":"猴·灵活","rooster":"鸡·精确","dog":"狗·忠诚","pig":"猪·厚重"
        }
        level_opts = {"human":"人级","earth":"地级","heaven":"天级"}
        with st.expander("选择挑战目标", expanded=False):
            z_type = st.selectbox("生肖", list(zodiac_opts.keys()), format_func=lambda x: zodiac_opts[x], label_visibility="collapsed", key="biz_type")
            z_level = st.selectbox("等级", list(level_opts.keys()), format_func=lambda x: level_opts[x], label_visibility="collapsed", key="biz_level")
            if st.button("⚔ 开始挑战", key="biz_start", use_container_width=True):
                _init_battle(z_type, z_level)
                set_phase("BATTLE")
                st.rerun()

    with col3:
        st.markdown("""
        <div class="hub-card">
            <div class="icon">💬</div>
            <div class="name">寻求指导</div>
            <div class="desc">向角色请教知识</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("💬 学习请教", key="hub_learn", use_container_width=True):
            set_phase("LEARNING")
            st.rerun()

    with col4:
        st.markdown("""
        <div class="hub-card">
            <div class="icon">🏛</div>
            <div class="name">势力</div>
            <div class="desc">管理阵营关系</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🏛 势力管理", key="hub_faction", use_container_width=True):
            set_phase("FACTIONS")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # 第二行
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        if st.button("✨ 回响查看", key="hub_rev", use_container_width=True):
            set_phase("REVERBERATIONS")
            st.rerun()

    with col6:
        st.markdown("""
        <div class="hub-card">
            <div class="icon">📚</div>
            <div class="name">知识副本</div>
            <div class="desc">上传文档·生成试炼</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📚 知识副本", key="hub_dungeon", use_container_width=True):
            set_phase("DUNGEON")
            st.rerun()

    # 势力声望摘要
    st.markdown("""
    <div class="section-title" style="margin-top:1.2rem;">
        势力声望
        <span class="en">FACTION REPUTATION</span>
    </div>
    """, unsafe_allow_html=True)
    rep_cols = st.columns(4)
    factions = [("heaven_gate", "天堂口"), ("extremist", "极道"), ("fortune", "貔貅"), ("shadow", "猫")]
    fcolors = ["#C49248", "#EF4444", "#22D3EE", "#A78BFA"]
    for i, (fid, fname) in enumerate(factions):
        with rep_cols[i]:
            rep = state.player.faction_reputation.get(fid, 0)
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(196,146,72,0.12); border-radius:10px; padding:14px; text-align:center;">
                <div style="font-size:0.7rem; color:#8E879A; letter-spacing:0.1em; margin-bottom:4px;">{fname}</div>
                <div style="font-size:1.3rem; font-weight:800; color:{fcolors[i]};">{rep}</div>
            </div>
            """, unsafe_allow_html=True)

# ===== 战斗 =====
def _init_battle(zodiac_type: str = "rat", zodiac_level: str = "human"):
    """初始化战斗系统"""
    engine = st.session_state.engine
    if not engine:
        return

    bi = BattleIntegrator(engine.state)
    # 连接 RAG 引擎 + LLM 用于真实题目生成
    try:
        rag = get_rag_engine()
        if rag:
            bi.connect_to_rag(rag)
            if hasattr(rag, 'llm') and rag.llm:
                bi.set_llm(rag.llm)
    except Exception:
        pass
    bi.start_battle_with_bank(zodiac_type, zodiac_level)
    st.session_state.battle_integrator = bi

def render_battle():
    bi = st.session_state.battle_integrator
    if not bi:
        set_phase("EXPLORATION")
        st.rerun()
        return

    info = bi.get_battle_info()
    question = bi.get_current_question()

    # 战斗标题
    zodiac_display = {
        "rat": "鼠·智慧", "ox": "牛·力量", "tiger": "虎·威猛", "dragon": "龙·全面",
        "snake": "蛇·阴柔", "horse": "马·速度", "sheep": "羊·温顺", "monkey": "猴·灵活",
        "rooster": "鸡·精确", "dog": "狗·忠诚", "pig": "猪·厚重", "rabbit": "兔·敏捷"
    }
    ztype = info.get("zodiac_type", "rat")
    zlevel = info.get("zodiac_level", "human")
    zname = zodiac_display.get(ztype, ztype)
    level_name = {"human": "人级", "earth": "地级", "heaven": "天级"}.get(zlevel, "人级")

    st.markdown(f"""
    <div class="battle-header">
        <div><span class="battle-level-tag {zlevel}">{level_name}</span></div>
        <div class="battle-zodiac">⚔ {zname} ⚔</div>
        <div style="color:#666; font-size:0.85rem;">
            需答对 {info.get("required_rate", "100%")}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not question:
        # 无题目 → 战斗结束
        result = bi.battle._calculate_result()
        st.session_state.battle_result = result
        set_phase("BATTLE_RESULT")
        st.rerun()
        return

    q = question

    # 题目
    st.markdown(f"""
    <div class="q-container">
        <div class="q-text">{q.get("content", "")}</div>
    </div>
    """, unsafe_allow_html=True)

    # 选项
    options = q.get("options", [])
    option_labels = ["A", "B", "C", "D"]
    for i, opt in enumerate(options):
        label = option_labels[i] if i < len(option_labels) else str(i)
        if st.button(f"{label}. {opt}", key=f"battle_ans_{i}", use_container_width=True):
            result = bi.submit_answer(label)
            if result.get("battle_result"):
                st.session_state.battle_result = result["battle_result"]
                set_phase("BATTLE_RESULT")
            st.rerun()

    # 进度
    remaining = q.get("remaining", 1)
    correct = q.get("correct_count", 0)
    total = info.get("total_questions", 3)
    st.markdown(f'<div class="q-progress"><span>剩余 {remaining} 题</span><span>正确 {correct}/{total}</span></div>', unsafe_allow_html=True)

    # 投降
    if st.button("🏳️ 认输", key="battle_surrender"):
        bi.battle.surrender()
        if st.session_state.engine:
            st.session_state.engine.state.progression.story_flags["in_battle"] = False
        auto_save()
        set_phase("EXPLORATION")
        st.session_state.battle_integrator = None
        st.rerun()

def render_battle_result():
    result = st.session_state.get("battle_result")
    if not result:
        set_phase("EXPLORATION")
        st.rerun()
        return

    if result.victory:
        st.markdown(f"""
        <div class="battle-result-box win">
            <div class="result-icon">✦</div>
            <div style="font-size:2rem; color:#00ff00; text-shadow:0 0 30px rgba(0,255,0,0.3);">胜 利</div>
            <div class="result-text">正确 {result.correct_count}/{result.total_questions}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="battle-result-box lose">
            <div class="result-icon">✗</div>
            <div style="font-size:2rem; color:#ff0000; text-shadow:0 0 30px rgba(255,0,0,0.3);">失 败</div>
            <div class="result-text">正确 {result.correct_count}/{result.total_questions}</div>
        </div>
        """, unsafe_allow_html=True)

    # 奖励
    if result.rewards:
        rew = result.rewards
        st.markdown("##### 获得奖励")
        rcols = st.columns(3)
        if "dao" in rew:
            rcols[0].success(f"道 +{rew['dao']}")
        if "exp" in rew:
            rcols[1].info(f"经验 +{rew['exp']}")
        if result.perfect_clear:
            rcols[2].success("完美通关！")
        # 应用奖励
        bi = st.session_state.battle_integrator
        if bi:
            bi.battle.apply_rewards(result)
            auto_save()

    st.markdown("---")
    if st.button("📖 返回", use_container_width=True):
        # 清除战斗标记防止循环
        if st.session_state.engine:
            st.session_state.engine.state.progression.story_flags["in_battle"] = False
        st.session_state.battle_integrator = None
        st.session_state.battle_result = None
        # 回到剧情或探索
        if st.session_state.engine and st.session_state.engine.current_scene:
            set_phase("STORY")
        else:
            set_phase("EXPLORATION")
        st.rerun()

# ===== 学习请教 =====
# ---- 角色显示配置 ----
ROLE_DISPLAY = {
    "qixia": {
        "name": "齐夏", "title": "终局推演者", "avatar": "🧑‍💼",
        "desc": "擅长从规则漏洞中寻找生路，适合复杂问题拆解、策略判断与逆向分析。冷静理性，直指本质。"
    },
    "chutianqiu": {
        "name": "楚天秋", "title": "逻辑框架师", "avatar": "🎯",
        "desc": "天堂口首领，擅长整合资源、拆解混乱信息，并将问题整理成可执行的推演路径。领袖气质，条理分明。"
    },
    "joe_gajin": {
        "name": "乔家劲", "title": "行动执行者", "avatar": "💪",
        "desc": "信奉「干就完了」的行动派，擅长实战操作、快速决策与即时反馈。简单粗暴，效率至上。"
    },
}


def render_chat_message(msg_role: str, content: str, display_name: str = ""):
    """使用 st.chat_message 渲染聊天消息（Streamlit 原生管理 DOM，避免冲突）"""
    with st.chat_message(msg_role):
        if display_name:
            st.markdown(f"**{display_name}**\n\n{content}")
        else:
            st.markdown(content)


def render_learning():
    rag = get_rag_engine()
    kb_id = st.session_state.kb_id

    # ===== 回响接入面板 =====
    st.markdown("""
    <div class="section-title">
        回响接入
        <span class="en">RESONANCE ACCESS</span>
    </div>
    """, unsafe_allow_html=True)

    all_roles = get_all_roles()
    role_opts = [r.value for r in all_roles]
    current_idx = role_opts.index(st.session_state.role) if st.session_state.role in role_opts else 0

    left, right = st.columns([1.3, 1])
    with left:
        selected_role = st.selectbox(
            "回响角色", role_opts, index=current_idx,
            format_func=lambda x: ROLE_DISPLAY.get(x, {}).get("name", x),
            label_visibility="collapsed",
            key="learning_role_selector"
        )
        if selected_role != st.session_state.role:
            switch_rag_role(selected_role)
            st.rerun()
    with right:
        role_key = st.session_state.role
        display = ROLE_DISPLAY.get(role_key, {})
        st.markdown(f"""
        <div class="role-card">
            <div class="badge">CURRENT RESONANCE</div>
            <div class="name">{display.get('avatar', '')} {display.get('name', role_key)}</div>
            <div class="title">{display.get('title', '')}</div>
            <div class="desc">{display.get('desc', '')}</div>
        </div>
        """, unsafe_allow_html=True)

    # ===== 审判对话 =====
    st.markdown("""
    <div class="section-title">
        审判对话
        <span class="en">TRIAL DIALOGUE</span>
    </div>
    """, unsafe_allow_html=True)

    msgs = get_messages(st.session_state.messages, kb_id, st.session_state.role)

    if not msgs:
        st.markdown("""
        <div class="chat-empty">
            暂无试炼记录。<br>
            提出第一个问题，唤醒你的回响。
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in msgs[-10:]:
            role_key = msg["role"]
            content = msg["content"]
            if role_key == "user":
                render_chat_message("user", content)
            else:
                display = ROLE_DISPLAY.get(role_key, {})
                dn = f"{display.get('avatar', '')} {display.get('name', role_key)} · {display.get('title', '回响推演')}"
                render_chat_message("assistant", content, dn)

    # ===== 请求处理 =====
    prompt = st.chat_input("输入你的求生问题，向回响发起推演……", key="learning_chat_input")

    if prompt:
        if "messages" not in st.session_state:
            st.session_state.messages = {}
        # 先渲染用户消息（同一渲染周期内，不 rerun）
        render_chat_message("user", prompt)
        # 保存用户消息
        add_message(st.session_state.messages, kb_id, st.session_state.role, {"role": "user", "content": prompt})
        # 生成并渲染 AI 回复（同步，同一渲染周期）
        if rag:
            with st.spinner("回响推演中..."):
                response = ""
                for chunk in rag.query(prompt):
                    response += chunk
            display = ROLE_DISPLAY.get(st.session_state.role, {})
            dn = f"{display.get('avatar', '')} {display.get('name', st.session_state.role)} · {display.get('title', '回响推演')}"
            render_chat_message("assistant", response, dn)
            add_message(st.session_state.messages, kb_id, st.session_state.role, {"role": st.session_state.role, "content": response})
        save_messages(st.session_state.messages)
        # 不调用 st.rerun() — 让 Streamlit 自动 rerun

    st.markdown("---")
    if st.button("🏛 返回道城", use_container_width=True):
        set_phase("EXPLORATION")
        st.rerun()

# ===== 势力管理 =====
def render_factions():
    engine = st.session_state.engine
    if not engine:
        return

    state = engine.state
    fm = FactionManager(state)

    st.markdown("""
    <div class="section-title">
        四大势力
        <span class="en">FACTIONS</span>
    </div>
    """, unsafe_allow_html=True)

    faction_data = [
        ("heaven_gate", "天堂口", "团结协作，共同逃离", "楚天秋", "🤝"),
        ("extremist", "极道", "以力量打破规则", "燕知春", "💪"),
        ("fortune", "貔貅", "智慧敛财，利益至上", "钱 Meck", "💰"),
        ("shadow", "猫", "暗中行动，积蓄力量", "陈俊南", "🐱"),
    ]

    cols = st.columns(2)
    for i, (fid, fname, desc, leader, icon) in enumerate(faction_data):
        with cols[i % 2]:
            rep = state.player.faction_reputation.get(fid, 0)
            is_member = state.player.faction == fid
            border = "#d4a574" if is_member else "#2a2a4a"
            glow = "0 0 20px rgba(212,165,116,0.2)" if is_member else "none"

            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#12121f,#1a1a30); border:1px solid {border};
                        border-radius:12px; padding:18px; margin:10px 0;
                        box-shadow:{glow};">
                <div style="font-size:1.1rem; color:#d4a574;">{icon} {fname}</div>
                <div style="color:#888; font-size:0.85rem; margin:6px 0;">{desc}</div>
                <div style="color:#666; font-size:0.8rem;">领袖：{leader}</div>
                <div style="color:#9370db; font-size:0.85rem; margin-top:6px;">声望：{rep}</div>
            </div>
            """, unsafe_allow_html=True)

            if is_member:
                st.info("✅ 你已加入")
                fmr = FactionManager(state)
                quests = fmr.get_available_quests()
                if quests:
                    with st.expander("📋 当前任务"):
                        for q in quests:
                            st.markdown(f"- **{q['title']}**: {q['description']}")
            elif state.player.faction is None:
                if st.button(f"加入 {fname}", key=f"join_{fid}", use_container_width=True):
                    can_join, unmet = fm.check_join_conditions(fid)
                    if can_join:
                        fm.join_faction(fid)
                        auto_save()
                        st.success(f"已加入 {fname}！")
                        st.rerun()
                    else:
                        st.warning(f"条件不足: {', '.join(unmet)}")

    st.markdown("---")
    if st.button("🏛 返回道城", use_container_width=True):
        set_phase("EXPLORATION")
        st.rerun()

# ===== 回响查看 =====
def render_reverberations():
    engine = st.session_state.engine
    if not engine:
        return

    rs = ReverberationSystem(engine.state)
    progress = rs.get_all_progress()

    st.markdown("""
    <div class="section-title">
        回响 · 觉醒之力
        <span class="en">REVERBERATIONS</span>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(2)
    for i, rev in enumerate(progress["reverberations"]):
        with cols[i % 2]:
            level = rev["level"]
            cls = "rev-card active" if level > 0 else "rev-card"
            st.markdown(f"""
            <div class="{cls}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="rname">{rev['name']}</span>
                    <span class="rlevel">{'✦' * level}{'◇' * (rev['max_level'] - level)} Lv.{level}</span>
                </div>
                <div class="rdesc">{rev['description']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="end-divider"></div>', unsafe_allow_html=True)
    st.markdown("##### 觉醒追踪")
    trackers = progress.get("trackers", {})
    tcols = st.columns(3)
    with tcols[0]:
        st.info(f"📚 连续复习: {trackers.get('review_streak', 0)}/3")
        st.info(f"🏆 连续正确: {trackers.get('correct_answer_streak', 0)}/50")
    with tcols[1]:
        st.warning(f"💥 难题连解: {trackers.get('hard_question_streak', 0)}/3")
        st.warning(f"❌ 答错: {trackers.get('wrong_answer_total', 0)}/10")
    with tcols[2]:
        st.success(f"📖 学习天数: {trackers.get('learning_day_streak', 0)}/7")
        st.success(f"🧠 基础掌握: {trackers.get('basic_mastered_count', 0)}/10")

    st.markdown("---")
    if st.button("🏛 返回道城", use_container_width=True):
        set_phase("EXPLORATION")
        st.rerun()

# ===== 副本系统 =====

def _get_dungeon_generator():
    """获取或创建 DungeonGenerator"""
    if st.session_state.dungeon_generator is None:
        rag = get_rag_engine()
        llm = rag.llm if rag else None
        st.session_state.dungeon_generator = DungeonGenerator(llm=llm)
    return st.session_state.dungeon_generator


def _generate_dungeon_character_reply(char_role: str, knowledge_seed: str, user_input: str, history: list) -> str:
    """生成角色回复（LLM + mock 两级回退）"""
    role_configs = {
        "qixia": {"name": "齐夏", "avatar": "🧑‍💼",
                   "style": "你极度理性、稳定、克制。你只做一件事：让问题收敛。不废话，直接指向本质。"},
        "chutianqiu": {"name": "楚天秋", "avatar": "🎯",
                        "style": "你擅长构建逻辑框架，条理清晰。你把复杂问题拆解成体系，用结构化方式呈现。"},
        "joe_gajin": {"name": "乔家劲", "avatar": "💪",
                       "style": "你行动派，信奉「干就完了」。直接给可执行的操作，不绕弯子，简单粗暴有效。"},
    }
    cfg = role_configs.get(char_role, role_configs["qixia"])

    # 尝试 LLM
    rag = get_rag_engine()
    if rag and hasattr(rag, 'llm') and rag.llm:
        try:
            from langchain_core.messages import HumanMessage
            history_text = ""
            for msg in history[-4:]:
                speaker = msg.get("speaker", cfg["name"])
                history_text += f"{speaker}: {msg['content']}\n"

            prompt = f"""你是{cfg['name']}。{cfg['style']}

背景知识：{knowledge_seed}

当前对话上下文：
{history_text}

用户说：{user_input}

请以{cfg['name']}的身份，基于背景知识，用1-3句话回复用户。
保持角色风格，自然口语化，不要用模板套路句式。"""

            messages = [HumanMessage(content=prompt)]
            response = rag.llm.invoke(messages)
            text = response.content if hasattr(response, 'content') else str(response)
            if text and len(text) > 5:
                return text.strip()
        except Exception:
            pass

    # 回退到 mock 模板
    mock_replies = {
        "qixia": f"别管那些花哨的。核心在于——{knowledge_seed[:40]}……先把本质拎清楚。",
        "chutianqiu": f"我来梳理一下。基于这段知识，可以分三层理解：第一，{knowledge_seed[:30]}……第二，看它和整体有什么关系。第三，落到具体的应用场景。",
        "joe_gajin": f"说那么多干啥？来，{knowledge_seed[:30]}……先搞一个试试看，干就完了。",
    }
    return mock_replies.get(char_role, mock_replies["qixia"])


def _generate_dungeon_trio_speech(char_role: str, knowledge_seed: str) -> str:
    """生成三角定调发言（LLM + mock 两级回退）"""
    role_configs = {
        "qixia": {"name": "齐夏", "style": "极度理性、克制。一句话收敛问题的本质方向。"},
        "chutianqiu": {"name": "楚天秋", "style": "逻辑严密，用框架化语言拆解知识结构。"},
        "joe_gajin": {"name": "乔家劲", "style": "行动派，给出可执行的具体操作指令。"},
    }
    cfg = role_configs.get(char_role, role_configs["qixia"])

    rag = get_rag_engine()
    if rag and hasattr(rag, 'llm') and rag.llm:
        try:
            from langchain_core.messages import HumanMessage
            prompt = f"""你是{cfg['name']}。{cfg['style']}

你身处终焉之地，面对一个包含以下知识的场景：
{knowledge_seed}

请以{cfg['name']}的身份，用一句话点明这个知识的{char_role}。
- 齐夏：收敛到本质，指出最关键的一点
- 楚天秋：给出一个结构化的框架视角
- 乔家劲：告诉玩家具体该怎么做

直接输出你的话，不要加引号或前缀。"""

            messages = [HumanMessage(content=prompt)]
            response = rag.llm.invoke(messages)
            text = response.content if hasattr(response, 'content') else str(response)
            if text and len(text) > 5:
                return text.strip()
        except Exception:
            pass

    mock_speeches = {
        "qixia": f"别管场景什么样。核心是——{knowledge_seed[:30]}…先把本质拎清楚。",
        "chutianqiu": f"我来梳理一下。这个知识可以分三层结构——第一，{knowledge_seed[:20]}…第二，理解其内在逻辑。第三，应用到实际场景。",
        "joe_gajin": f"说那么多干啥？来，先动手搞一下试试看。实践出真知，干就完了。",
    }
    return mock_speeches.get(char_role, mock_speeches["qixia"])


def render_dungeon_entrance():
    """知识副本入口：上传文档 + 生成副本"""
    engine = st.session_state.engine
    if not engine:
        st.info("请先进入终焉之地")
        return

    st.markdown("""
    <div class="section-title">
        知识副本
        <span class="en">KNOWLEDGE DUNGEON</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div style="color:#AFA89C; font-size:0.85rem; margin-bottom:20px; border-left:2px solid rgba(196,146,72,0.15); padding-left:12px;">上传你的学习资料，将其转化为终焉之地的试炼副本</div>', unsafe_allow_html=True)

    # 检查是否有进行中的副本
    if engine.has_active_dungeon():
        manifest = engine.current_dungeon
        progress = f"{engine.dungeon_scene_index + 1}/{manifest.scene_count}"
        st.info(f"📖 正在进行: {manifest.dungeon_name} ({progress})")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶ 继续攻略", use_container_width=True):
                st.session_state.game_phase = "DUNGEON_SCENE"
                st.rerun()
        with col2:
            if st.button("❌ 放弃副本", use_container_width=True):
                engine.clear_dungeon()
                st.rerun()

    st.markdown('<div class="end-divider"></div>', unsafe_allow_html=True)

    # 上传区域
    uploaded = st.file_uploader(
        "上传知识文档（.txt / .md / .pdf）",
        type=["txt", "md", "pdf"],
        key="dungeon_file_upload"
    )

    if uploaded:
        from core.document_parser import DocumentParser
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded.name.split('.')[-1]}") as tmp:
            tmp.write(uploaded.getvalue())
            tmp_path = tmp.name
        try:
            text = DocumentParser.parse(tmp_path)
            st.session_state.dungeon_loaded_kb_text = text
            # 预览
            preview = text[:300] + "..." if len(text) > 300 else text
            st.markdown(f'<div style="background:#0a0a12; border:1px solid #2a2a3a; border-radius:10px; padding:16px; margin:12px 0; color:#aaa; font-size:0.85rem; max-height:200px; overflow-y:auto;">{preview}</div>', unsafe_allow_html=True)
            st.caption(f"📄 {uploaded.name} · 约 {len(text)} 字")
        except Exception as e:
            st.error(f"❌ 解析失败: {e}")
            os.unlink(tmp_path)
            return
        os.unlink(tmp_path)

        # 生成副本按钮
        kb_id = st.session_state.kb_id
        kb_manager = st.session_state.kb_manager
        kb_obj = kb_manager.get_kb(kb_id)
        kb_name = kb_obj.name if kb_obj else uploaded.name

        if st.button("🔥 生成副本", use_container_width=True, type="primary"):
            with st.spinner("副本生成中...（5-15秒）"):
                generator = _get_dungeon_generator()
                cycle = engine.state.progression.cycle_count + 1
                manifest = generator.generate(
                    kb_text=text,
                    kb_id=kb_id,
                    kb_name=kb_name,
                    cycle_count=cycle,
                )
                engine.load_dungeon(manifest)
                st.session_state.dungeon_manifest = manifest
                st.session_state.dungeon_initial_shown = False
                st.session_state.dungeon_chat_history = []
                st.session_state.dungeon_reward_given = False
                st.session_state.game_phase = "DUNGEON_SCENE"
                st.rerun()

    st.markdown("---")
    if st.button("🏛 返回道城", use_container_width=True):
        set_phase("EXPLORATION")
        st.rerun()


def render_dungeon_scene():
    """副本场景：群像对话主界面"""
    engine = st.session_state.engine
    if not engine:
        set_phase("EXPLORATION")
        st.rerun()
        return

    scene = engine.get_current_dungeon_scene()
    if not scene:
        # 副本已完成
        set_phase("DUNGEON_COMPLETE")
        st.rerun()
        return

    manifest = engine.current_dungeon
    total = manifest.scene_count if manifest else 1
    current = engine.dungeon_scene_index + 1

    # 标题
    st.markdown(f"""
    <div class="section-title">
        {manifest.dungeon_name if manifest else "副本"} · 场景 {current}/{total}
        <span class="en">DUNGEON TRIAL</span>
    </div>
    """, unsafe_allow_html=True)

    # 环境描述
    st.markdown(f"""
    <div style="background:#0a0a12; border:1px solid #2a2a3a; border-radius:12px; padding:20px; margin-bottom:16px;">
        <div style="color:#d4a574; font-size:0.8rem; letter-spacing:2px; margin-bottom:4px;">📍 {scene.location}</div>
        <div style="color:#888; font-size:0.9rem; line-height:1.7;">{scene.atmosphere}</div>
        <div style="margin-top:12px; padding:12px; border-left:3px solid #8b6914; background:#0d0d0a; border-radius:0 8px 8px 0;">
            <div style="color:#c4a050; font-size:0.85rem; font-style:italic; line-height:1.7;">{scene.knowledge_seed}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ===== Phase 1: 三角定调 =====
    if not st.session_state.dungeon_initial_shown:
        st.markdown("""
        <div class="section-title">
            回响接入 · 三角定调
            <span class="en">TRIO RESONANCE</span>
        </div>
        """, unsafe_allow_html=True)

        for char_id, char_info in [
            ("qixia", ("🧑‍💼", "齐夏")),
            ("chutianqiu", ("🎯", "楚天秋")),
            ("joe_gajin", ("💪", "乔家劲")),
        ]:
            speech = _generate_dungeon_trio_speech(char_id, scene.knowledge_seed)
            st.markdown(f"""
            <div class="npc-box" style="border-left-color:{'rgba(196,146,72,0.6)' if char_id == 'qixia' else 'rgba(139,92,246,0.6)' if char_id == 'chutianqiu' else 'rgba(34,197,94,0.6)'};">
                <div class="name">{char_info[0]} {char_info[1]}</div>
                <div class="line">{speech}</div>
            </div>
            """, unsafe_allow_html=True)

        if st.button("📖 开始对话", use_container_width=True, type="primary"):
            st.session_state.dungeon_initial_shown = True
            st.session_state.dungeon_selected_char = "qixia"
            st.session_state.dungeon_chat_history = []
            st.rerun()
        return

    # ===== Phase 2: 自由发散 =====
    st.markdown("""
    <div class="section-title">
        自由推演
        <span class="en">FREE DEDUCTION</span>
    </div>
    """, unsafe_allow_html=True)

    # 聊天记录
    for msg in st.session_state.dungeon_chat_history[-10:]:
        is_user = (msg["role"] == "user")
        if is_user:
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:
            speaker = msg.get("speaker", "回响角色")
            with st.chat_message("assistant"):
                st.markdown(f"**{speaker}**\n\n{msg['content']}")

    # 角色切换
    char_cols = st.columns(3)
    char_options = [
        ("qixia", "🧑‍💼 齐夏", "理性收敛"),
        ("chutianqiu", "🎯 楚天秋", "框架梳理"),
        ("joe_gajin", "💪 乔家劲", "行动实操"),
    ]
    for i, (cid, label, hint) in enumerate(char_options):
        with char_cols[i]:
            is_selected = st.session_state.dungeon_selected_char == cid
            border_color = "#d4a574" if is_selected else "#2a2a4a"
            if st.button(
                f"{'▸' if is_selected else ' '} {label}\n{hint}",
                key=f"dungeon_char_{cid}",
                use_container_width=True,
            ):
                st.session_state.dungeon_selected_char = cid
                st.rerun()

    # 输入框
    user_input = st.chat_input(f"对{ {'qixia':'齐夏','chutianqiu':'楚天秋','joe_gajin':'乔家劲'}.get(st.session_state.dungeon_selected_char,'')}说...")
    if user_input:
        # 渲染用户消息（同一渲染周期）
        with st.chat_message("user"):
            st.markdown(user_input)
        # 保存用户消息
        st.session_state.dungeon_chat_history.append({
            "role": "user",
            "content": user_input,
            "speaker": "觉醒者",
        })

        # 生成并渲染角色回复（同一渲染周期）
        char_name_map = {"qixia": "齐夏", "chutianqiu": "楚天秋", "joe_gajin": "乔家劲"}
        char_avatar_map = {"qixia": "🧑‍💼", "chutianqiu": "🎯", "joe_gajin": "💪"}
        cid = st.session_state.dungeon_selected_char
        with st.spinner(f"{char_name_map.get(cid, '')}思考中..."):
            reply = _generate_dungeon_character_reply(
                cid, scene.knowledge_seed, user_input, st.session_state.dungeon_chat_history
            )
        avatar = char_avatar_map.get(cid, "")
        name = char_name_map.get(cid, "")
        speaker = f"{avatar} {name}"
        with st.chat_message("assistant"):
            st.markdown(f"**{speaker}**\n\n{reply}")
        st.session_state.dungeon_chat_history.append({
            "role": "assistant",
            "content": reply,
            "speaker": speaker,
        })
        # 不调用 st.rerun() — 让 Streamlit 自动 rerun

    # 继续按钮
    st.markdown("---")
    if st.button("▶ 继续 → 下一场景", use_container_width=True):
        engine.advance_dungeon_scene()
        st.session_state.dungeon_initial_shown = False
        st.session_state.dungeon_chat_history = []
        if engine.is_dungeon_complete():
            set_phase("DUNGEON_COMPLETE")
        st.rerun()


def render_dungeon_complete():
    """副本结算"""
    engine = st.session_state.engine
    if not engine:
        set_phase("EXPLORATION")
        st.rerun()
        return

    manifest = st.session_state.dungeon_manifest or engine.current_dungeon
    name = manifest.dungeon_name if manifest else "知识副本"

    st.markdown(f"""
    <div style="text-align:center; padding:60px 20px;">
        <div style="font-size:3rem; margin-bottom:20px;">✦</div>
        <div style="font-size:1.2rem; color:#8b0000; letter-spacing:4px; margin-bottom:8px;">副本完成</div>
        <div style="font-size:1.8rem; color:#d4a574; letter-spacing:6px; text-shadow:0 0 20px rgba(212,165,116,0.3);">{name}</div>
        <div style="width:80px; height:1px; background:linear-gradient(90deg,transparent,#d4a574,transparent); margin:24px auto;"></div>
        <div style="color:#ffd700; font-size:1.5rem; text-shadow:0 0 20px rgba(255,215,0,0.3);">道 +50</div>
        <div style="color:#666; font-size:0.85rem; margin-top:8px;">知识之力已融入你的灵魂</div>
    </div>
    """, unsafe_allow_html=True)

    # 发放奖励（仅一次）
    if not st.session_state.dungeon_reward_given:
        engine.state.player.dao += 50
        st.session_state.dungeon_reward_given = True
        auto_save()

    # 清除副本状态
    engine.clear_dungeon()
    st.session_state.dungeon_manifest = None
    st.session_state.dungeon_initial_shown = False
    st.session_state.dungeon_chat_history = []

    if st.button("🏛 返回道城", use_container_width=True, type="primary"):
        set_phase("EXPLORATION")
        st.rerun()


# ===== 日过渡动画 =====
def render_day_transition():
    dt = st.session_state.get("day_transition")
    if not dt:
        set_phase("EXPLORATION")
        st.rerun()
        return

    day = dt["day"]
    title = dt["title"]

    day_quotes = {
        2: "你睁开眼睛，发现自己还在终焉之地。\n但今天的你，已经不一样了。",
        3: "体内的道在流动……\n你隐约感觉到，某种力量正在苏醒。",
        4: "道城的钟声敲响。\n今天，你必须做出选择。",
        5: "攻城战的号角已经吹响。\n知识城池，就在前方。",
        6: "暗流在涌动。\n势力之间的平衡，即将被打破。",
        7: "信任与背叛，只在一念之间。\n今天，你可能会失去什么。",
        8: "天级的领域已经打开。\n真正的考验，现在才开始。",
        9: "倒计时。\n明天，一切将迎来终结。",
        10: "最终之日。\n终焉降临。",
    }

    st.markdown(f"""
    <div class="day-transition">
        <div style="font-size:0.85rem; color:#8b0000; letter-spacing:4px; margin-bottom:10px;">
            ——— 第 {day-1 if day > 1 else 0} 日 结 束 ———
        </div>
        <div class="day-number">第 {day} 日</div>
        <div class="day-title">「{title}」</div>
        <div class="day-quote">{day_quotes.get(day, "")}</div>
        <div style="margin-top:40px; width:100px; height:1px; background:#3a3a5a;"></div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔥 进入第" + str(day) + "日", use_container_width=True):
        engine = get_engine()
        engine.next_day()
        auto_save()
        set_phase("STORY")
        st.session_state.day_transition = None
        st.rerun()

# ===== 主渲染逻辑 =====
def main():
    inject_css()
    init_session()
    render_sidebar()

    # 通知
    if st.session_state.notification:
        st.markdown(f'<div class="notification">{st.session_state.notification}</div>', unsafe_allow_html=True)
        st.session_state.notification = None

    # 回响觉醒检测
    if st.session_state.engine and st.session_state.game_phase not in ("LANDING", "DAY_TRANSITION"):
        current_revs = len([r for r in st.session_state.engine.state.player.reverberations if "_lv" in r])
        if current_revs > st.session_state.last_rev_count and current_revs > 0:
            new_rev_name = st.session_state.engine.state.player.reverberations[-1]
            st.session_state.new_rev_notification = {
                "name": new_rev_name.split("_lv")[0] if "_lv" in new_rev_name else new_rev_name,
                "level": 1,
                "description": "新的回响之力已在你的体内觉醒..."
            }
            st.session_state.last_rev_count = current_revs

    # 回响觉醒弹窗
    if st.session_state.new_rev_notification:
        notif = st.session_state.new_rev_notification
        st.markdown(f"""
        <div class="rev-awakening">
            <div class="rev-icon">✦</div>
            <div class="rev-title">回 响 觉 醒</div>
            <div class="rev-name">{notif.get('name', '???')}</div>
            <div style="color:#888; font-size:0.85rem;">Lv.{notif.get('level', 1)}</div>
            <div class="rev-desc">{notif.get('description', '')}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("✦ 感 受 力 量 ✦", key="dismiss_rev"):
            st.session_state.new_rev_notification = None
            st.rerun()

    # 标题
    st.markdown("""
    <div class="title-row">
        <div class="end-title">十日终焉<span class="sep">·</span>知识觉醒</div>
        <div class="title-english">Reincarnation Trial System</div>
    </div>
    <div class="end-subtitle">每一次提问，都是一次轮回中的求生。</div>
    <div class="end-divider"></div>
    """, unsafe_allow_html=True)

    # 状态栏
    if st.session_state.engine and st.session_state.game_phase != "LANDING":
        render_status_bar()

    # 阶段路由
    phase = st.session_state.game_phase

    if phase == "LANDING":
        render_landing()
    elif phase == "DAY_TRANSITION":
        render_day_transition()
    elif phase == "STORY":
        render_story()
    elif phase == "EXPLORATION":
        render_exploration()
    elif phase == "BATTLE":
        render_battle()
    elif phase == "BATTLE_RESULT":
        render_battle_result()
    elif phase == "LEARNING":
        render_learning()
    elif phase == "FACTIONS":
        render_factions()
    elif phase == "REVERBERATIONS":
        render_reverberations()
    elif phase == "DUNGEON":
        render_dungeon_entrance()
    elif phase == "DUNGEON_SCENE":
        render_dungeon_scene()
    elif phase == "DUNGEON_COMPLETE":
        render_dungeon_complete()
    else:
        render_landing()

if __name__ == "__main__":
    main()
