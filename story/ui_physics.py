# -*- coding: utf-8 -*-
"""
十日终焉 UI组件 - 物理交互动画
包含：3D卡片倾斜、水波纹、拖拽交互、弹性动画、鼠标跟随响应
"""

import streamlit as st


def init_physics_system():
    """初始化物理动画系统CSS和JS"""
    st.markdown("""
    <style>
    .physics-card {
        perspective: 1000px;
        transform-style: preserve-3d;
        transition: transform 0.15s ease-out;
    }
    .physics-card:hover {
        transform: translateZ(20px) rotateX(var(--rotate-x, 0deg)) rotateY(var(--rotate-y, 0deg));
    }
    .physics-card-content {
        transform: translateZ(30px);
        transition: transform 0.15s ease-out;
    }
    .wave-container {
        position: relative;
        overflow: hidden;
    }
    .wave-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(ellipse at center, rgba(139, 0, 0, 0.1) 0%, transparent 70%);
        animation: wave-pulse 3s ease-in-out infinite;
        pointer-events: none;
    }
    @keyframes wave-pulse {
        0%, 100% { transform: scale(0.8); opacity: 0.3; }
        50% { transform: scale(1.2); opacity: 0.6; }
    }
    .elastic-button {
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }
    .elastic-button:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 30px rgba(139, 0, 0, 0.3);
    }
    .elastic-button:active {
        transform: scale(0.95);
    }
    .draggable-region {
        cursor: grab;
        user-select: none;
    }
    .draggable-region:active {
        cursor: grabbing;
    }
    .spring-animation {
        animation: spring-bounce 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }
    @keyframes spring-bounce {
        0% { transform: scale(0.3); opacity: 0; }
        50% { transform: scale(1.1); }
        70% { transform: scale(0.95); }
        100% { transform: scale(1); opacity: 1; }
    }
    .magnetic-hover {
        transition: transform 0.4s ease;
    }
    .magnetic-hover:hover {
        transform: scale(1.05) translateY(-5px);
    }
    .ripple-effect {
        position: relative;
        overflow: hidden;
    }
    .ripple-effect::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        background: rgba(139, 0, 0, 0.3);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    .ripple-effect:active::after {
        width: 300px;
        height: 300px;
    }
    .tilt-wrapper {
        transform-style: preserve-3d;
        transition: transform 0.1s ease-out;
    }
    .noise-texture {
        position: relative;
    }
    .noise-texture::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
        opacity: 0.05;
        pointer-events: none;
        mix-blend-mode: overlay;
    }
    .glow-border {
        position: relative;
    }
    .glow-border::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #8b0000, #cc0000, #8b0000, #cc0000);
        background-size: 400% 400%;
        border-radius: inherit;
        animation: glow-flow 3s ease infinite;
        z-index: -1;
    }
    @keyframes glow-flow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .blur-reveal {
        filter: blur(10px);
        opacity: 0;
        animation: blur-in 0.8s ease forwards;
    }
    @keyframes blur-in {
        to { filter: blur(0); opacity: 1; }
    }
    .slide-up {
        transform: translateY(50px);
        opacity: 0;
        animation: slide-up-in 0.6s ease forwards;
    }
    @keyframes slide-up-in {
        to { transform: translateY(0); opacity: 1; }
    }
    .typewriter {
        overflow: hidden;
        white-space: nowrap;
        animation: type 2s steps(20, end);
    }
    @keyframes type {
        from { width: 0; }
        to { width: 100%; }
    }
    </style>
    
    <script>
    class PhysicsEngine {
        constructor() {
            this.cards = document.querySelectorAll('.physics-card');
            this.init();
        }
        
        init() {
            document.addEventListener('mousemove', (e) => this.handleMouseMove(e));
            this.initTiltCards();
            this.initRippleButtons();
        }
        
        initTiltCards() {
            const cards = document.querySelectorAll('.tilt-wrapper, .physics-card');
            cards.forEach(card => {
                card.addEventListener('mousemove', (e) => this.tiltCard(e, card));
                card.addEventListener('mouseleave', () => this.resetCard(card));
            });
        }
        
        tiltCard(e, card) {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / centerY * -10;
            const rotateY = (x - centerX) / centerX * 10;
            
            card.style.setProperty('--rotate-x', rotateX + 'deg');
            card.style.setProperty('--rotate-y', rotateY + 'deg');
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px)`;
        }
        
        resetCard(card) {
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0)';
        }
        
        initRippleButtons() {
            const buttons = document.querySelectorAll('.ripple-effect');
            buttons.forEach(btn => {
                btn.addEventListener('click', (e) => this.createRipple(e, btn));
            });
        }
        
        createRipple(e, button) {
            const rect = button.getBoundingClientRect();
            const ripple = document.createElement('span');
            ripple.style.left = (e.clientX - rect.left) + 'px';
            ripple.style.top = (e.clientY - rect.top) + 'px';
            ripple.style.position = 'absolute';
            ripple.style.width = '10px';
            ripple.style.height = '10px';
            ripple.style.background = 'rgba(139, 0, 0, 0.5)';
            ripple.style.borderRadius = '50%';
            ripple.style.transform = 'translate(-50%, -50%)';
            ripple.style.animation = 'ripple 0.6s ease-out forwards';
            button.appendChild(ripple);
            setTimeout(() => ripple.remove(), 600);
        }
        
        handleMouseMove(e) {
            const cards = document.querySelectorAll('.magnetic-hover');
            cards.forEach(card => {
                const rect = card.getBoundingClientRect();
                const centerX = rect.left + rect.width / 2;
                const centerY = rect.top + rect.height / 2;
                
                const distanceX = (e.clientX - centerX) / rect.width;
                const distanceY = (e.clientY - centerY) / rect.height;
                
                const moveX = distanceX * 20;
                const moveY = distanceY * 20;
                
                card.style.transform = `translate(${moveX}px, ${moveY}px)`;
            });
        }
    }
    
    window.physicsEngine = new PhysicsEngine();
    </script>
    """, unsafe_allow_html=True)


def render_3d_card(title: str, content: str, css_class: str = "physics-card"):
    """渲染3D倾斜卡片"""
    st.markdown(f"""
    <div class="{css_class}">
        <style>
        .{css_class} {{
            background: linear-gradient(145deg, #1a1a1a 0%, #0d0d0d 100%);
            border: 1px solid #2a2a2a;
            border-left: 3px solid #8b0000;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            transform-style: preserve-3d;
            transition: transform 0.15s ease-out;
        }}
        .{css_class}:hover {{
            border-left-color: #cc0000;
            box-shadow: 0 0 30px rgba(139, 0, 0, 0.2);
        }}
        </style>
        <h3 style="color: #cc0000; margin-bottom: 15px;">{title}</h3>
        <p style="color: #888; line-height: 1.8;">{content}</p>
    </div>
    """, unsafe_allow_html=True)


def render_wave_container(content: str):
    """渲染水波纹效果容器"""
    st.markdown(f"""
    <div class="wave-container">
        <style>
        .wave-container {{
            background: linear-gradient(135deg, #111 0%, #0a0a0a 100%);
            border: 1px solid #2a2a2a;
            border-radius: 12px;
            padding: 25px;
            position: relative;
            overflow: hidden;
        }}
        </style>
        {content}
    </div>
    """, unsafe_allow_html=True)


def render_elastic_button(label: str, key: str = None, css_class: str = "elastic-button"):
    """渲染弹性按钮"""
    btn_html = f"""
    <button class="{css_class}" style="
        background: linear-gradient(180deg, #1a1a1a 0%, #111 100%);
        color: #e8e8e8;
        border: 1px solid #3d0000;
        border-radius: 4px;
        padding: 12px 30px;
        cursor: pointer;
        font-family: 'Microsoft YaHei', sans-serif;
        letter-spacing: 2px;
    ">
        {label}
    </button>
    """
    return st.markdown(btn_html, unsafe_allow_html=True)


def render_glow_border(content: str):
    """渲染发光边框"""
    st.markdown(f"""
    <div class="glow-border" style="background: #1a1a1a; border-radius: 8px; padding: 20px;">
        <style>
        .glow-border {{
            position: relative;
            z-index: 1;
        }}
        </style>
        {content}
    </div>
    """, unsafe_allow_html=True)


def render_blur_reveal(content: str, delay: float = 0):
    """模糊显现动画"""
    st.markdown(f"""
    <div class="blur-reveal" style="animation-delay: {delay}s;">
        {content}
    </div>
    """, unsafe_allow_html=True)


def render_slide_up(content: str, delay: float = 0):
    """滑入动画"""
    st.markdown(f"""
    <div class="slide-up" style="animation-delay: {delay}s;">
        {content}
    </div>
    """, unsafe_allow_html=True)


def render_spring_animation(content: str):
    """弹性弹跳动画"""
    st.markdown(f"""
    <div class="spring-animation">
        {content}
    </div>
    """, unsafe_allow_html=True)


def render_noise_texture(content: str):
    """噪点纹理"""
    st.markdown(f"""
    <div class="noise-texture" style="position: relative; padding: 20px; background: #111;">
        {content}
    </div>
    """, unsafe_allow_html=True)


def render_magnetic_card(title: str, content: str):
    """磁吸效果卡片"""
    st.markdown(f"""
    <div class="magnetic-hover" style="
        background: linear-gradient(145deg, #1a1a1a 0%, #0d0d0d 100%);
        border: 1px solid #2a2a2a;
        border-left: 3px solid #8b0000;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
    ">
        <h3 style="color: #cc0000; margin-bottom: 15px;">{title}</h3>
        <p style="color: #888; line-height: 1.8;">{content}</p>
    </div>
    """, unsafe_allow_html=True)


def render_tilt_wrapper(content: str):
    """3D倾斜包装器"""
    st.markdown(f"""
    <div class="tilt-wrapper" style="
        transform-style: preserve-3d;
        transition: transform 0.1s ease-out;
    ">
        {content}
    </div>
    """, unsafe_allow_html=True)