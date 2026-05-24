# -*- coding: utf-8 -*-
"""
十日终焉 UI组件 - 粒子特效系统
包含：粒子漂浮、燃烧效果、鼠标跟随、血迹/尘埃粒子、重力下落
"""

import streamlit as st
import random
import math


def init_particle_system():
    """初始化粒子系统CSS和JS"""
    st.markdown("""
    <style>
    #particles-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 9998;
        overflow: hidden;
    }
    .particle {
        position: absolute;
        border-radius: 50%;
        pointer-events: none;
        animation: particle-float linear forwards;
    }
    @keyframes particle-float {
        0% { transform: translateY(0) rotate(0deg); opacity: 0; }
        10% { opacity: var(--particle-opacity, 0.8); }
        90% { opacity: var(--particle-opacity, 0.3); }
        100% { transform: translateY(-100vh) rotate(720deg); opacity: 0; }
    }
    .dust-particle {
        position: absolute;
        width: 2px;
        height: 2px;
        background: rgba(139, 0, 0, 0.4);
        border-radius: 50%;
        pointer-events: none;
        animation: dust-float linear infinite;
    }
    @keyframes dust-float {
        0% { transform: translateX(0) translateY(0); opacity: 0; }
        20% { opacity: 0.6; }
        80% { opacity: 0.2; }
        100% { transform: translateX(var(--drift-x, 20px)) translateY(-100vh); opacity: 0; }
    }
    .ember {
        position: absolute;
        width: 4px;
        height: 4px;
        background: radial-gradient(circle, #ff4500 0%, #8b0000 50%, transparent 100%);
        border-radius: 50%;
        pointer-events: none;
        animation: ember-rise ease-out infinite;
        box-shadow: 0 0 6px 2px rgba(255, 69, 0, 0.4);
    }
    @keyframes ember-rise {
        0% { transform: translateY(0) scale(1); opacity: 1; }
        50% { opacity: 0.8; }
        100% { transform: translateY(-300px) scale(0.3); opacity: 0; }
    }
    .blood-splatter {
        position: absolute;
        width: 8px;
        height: 8px;
        background: radial-gradient(ellipse, rgba(139, 0, 0, 0.8) 0%, rgba(139, 0, 0, 0.3) 60%, transparent 100%);
        border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
        pointer-events: none;
        animation: splatter-drop ease-in forwards;
    }
    @keyframes splatter-drop {
        0% { transform: translateY(0) scale(1); opacity: 1; }
        70% { transform: translateY(var(--drop-distance, 100px)) scale(0.8); opacity: 0.8; }
        100% { transform: translateY(var(--drop-distance, 100px)) scale(0.5); opacity: 0; }
    }
    .cursor-trail {
        position: absolute;
        width: 10px;
        height: 10px;
        background: radial-gradient(circle, rgba(139, 0, 0, 0.6) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
        animation: trail-fade 0.5s ease-out forwards;
    }
    @keyframes trail-fade {
        0% { transform: scale(1); opacity: 0.8; }
        100% { transform: scale(0.1); opacity: 0; }
    }
    .gravity-particle {
        position: absolute;
        width: 3px;
        height: 3px;
        background: rgba(139, 0, 0, 0.5);
        border-radius: 50%;
        pointer-events: none;
        animation: gravity-fall ease-in forwards;
    }
    @keyframes gravity-fall {
        0% { transform: translateY(0) rotate(0deg); opacity: 0.8; }
        100% { transform: translateY(100vh) rotate(360deg); opacity: 0; }
    }
    .glitch-text {
        animation: glitch 0.3s infinite;
    }
    @keyframes glitch {
        0% { transform: translate(0); }
        20% { transform: translate(-2px, 2px); }
        40% { transform: translate(-2px, -2px); }
        60% { transform: translate(2px, 2px); }
        80% { transform: translate(2px, -2px); }
        100% { transform: translate(0); }
    }
    .scan-line {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(139, 0, 0, 0.3), transparent);
        animation: scan 4s linear infinite;
        pointer-events: none;
        z-index: 9997;
    }
    @keyframes scan {
        0% { transform: translateY(-100%); opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { transform: translateY(100vh); opacity: 0; }
    }
    .noise-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
        opacity: 0.03;
        pointer-events: none;
        z-index: 9996;
    }
    .vignette {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(ellipse at center, transparent 0%, transparent 50%, rgba(0,0,0,0.4) 100%);
        pointer-events: none;
        z-index: 9995;
    }
    </style>
    
    <script>
    class ParticleEngine {
        constructor() {
            this.particles = [];
            this.container = null;
            this.mousePos = { x: -100, y: -100 };
            this.init();
        }
        
        init() {
            this.container = document.getElementById('particles-container') || this.createContainer();
            document.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        }
        
        createContainer() {
            const div = document.createElement('div');
            div.id = 'particles-container';
            document.body.appendChild(div);
            return div;
        }
        
        handleMouseMove(e) {
            this.mousePos.x = e.clientX;
            this.mousePos.y = e.clientY;
            this.createTrail(e.clientX, e.clientY);
        }
        
        createTrail(x, y) {
            if (!this.container) return;
            const trail = document.createElement('div');
            trail.className = 'cursor-trail';
            trail.style.left = (x - 5) + 'px';
            trail.style.top = (y - 5) + 'px';
            this.container.appendChild(trail);
            setTimeout(() => trail.remove(), 500);
        }
        
        createFloatingParticles(count = 15, type = 'dust') {
            for (let i = 0; i < count; i++) {
                setTimeout(() => this.spawnParticle(type), i * 200);
            }
        }
        
        spawnParticle(type = 'dust') {
            if (!this.container) return;
            const particle = document.createElement('div');
            particle.className = type === 'ember' ? 'ember' : 'dust-particle';
            
            const startX = Math.random() * window.innerWidth;
            const duration = 3 + Math.random() * 4;
            const driftX = (Math.random() - 0.5) * 50;
            
            particle.style.left = startX + 'px';
            particle.style.bottom = '-10px';
            particle.style.setProperty('--drift-x', driftX + 'px');
            particle.style.animationDuration = duration + 's';
            
            this.container.appendChild(particle);
            setTimeout(() => particle.remove(), duration * 1000);
        }
        
        createBloodSplatter(x, y, count = 5) {
            for (let i = 0; i < count; i++) {
                const splatter = document.createElement('div');
                splatter.className = 'blood-splatter';
                
                const offsetX = (Math.random() - 0.5) * 30;
                const offsetY = Math.random() * -50;
                const dropDistance = 50 + Math.random() * 100;
                
                splatter.style.left = (x + offsetX) + 'px';
                splatter.style.top = (y + offsetY) + 'px';
                splatter.style.setProperty('--drop-distance', dropDistance + 'px');
                
                this.container.appendChild(splatter);
                setTimeout(() => splatter.remove(), 1000);
            }
        }
        
        createGravityParticles(count = 10, originX = null) {
            const startX = originX || Math.random() * window.innerWidth;
            
            for (let i = 0; i < count; i++) {
                const particle = document.createElement('div');
                particle.className = 'gravity-particle';
                
                const offsetX = (Math.random() - 0.5) * 100;
                const delay = Math.random() * 2;
                const duration = 1 + Math.random() * 2;
                
                particle.style.left = (startX + offsetX) + 'px';
                particle.style.top = '-10px';
                particle.style.animationDelay = delay + 's';
                particle.style.animationDuration = duration + 's';
                
                this.container.appendChild(particle);
                setTimeout(() => particle.remove(), (delay + duration) * 1000);
            }
        }
    }
    
    window.particleEngine = new ParticleEngine();
    </script>
    
    <div id="particles-container"></div>
    <div class="scan-line"></div>
    <div class="noise-overlay"></div>
    <div class="vignette"></div>
    """, unsafe_allow_html=True)


def show_floating_particles(count: int = 15, particle_type: str = 'dust'):
    """显示漂浮粒子 (dust/ember)"""
    intensity_map = {'low': 8, 'medium': 15, 'high': 25}
    num = intensity_map.get(particle_type, count) if isinstance(particle_type, int) else count
    
    particle_class = 'dust-particle' if particle_type == 'dust' else 'ember'
    
    js_code = f"""
    <script>
    (function() {{
        const container = document.getElementById('particles-container');
        if (!container) return;
        
        const particleClass = '{particle_class}';
        const count = {num};
        
        for (let i = 0; i < count; i++) {{
            setTimeout(() => {{
                const particle = document.createElement('div');
                particle.className = particleClass;
                
                const startX = Math.random() * window.innerWidth;
                const duration = 3 + Math.random() * 4;
                const driftX = (Math.random() - 0.5) * 50;
                
                particle.style.left = startX + 'px';
                particle.style.bottom = '-10px';
                particle.style.setProperty('--drift-x', driftX + 'px');
                particle.style.setProperty('--particle-opacity', 0.3 + Math.random() * 0.5);
                particle.style.animationDuration = duration + 's';
                
                container.appendChild(particle);
                setTimeout(() => particle.remove(), duration * 1000);
            }}, i * 200);
        }}
    }})();
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)


def show_ember_particles(count: int = 10):
    """显示燃烧余烬效果"""
    show_floating_particles(count, 'ember')


def show_blood_effect(x: int, y: int, intensity: int = 5):
    """显示血迹飞溅效果"""
    st.markdown(f"""
    <script>
    (function() {{
        const container = document.getElementById('particles-container');
        if (!container) return;
        
        const count = {intensity};
        for (let i = 0; i < count; i++) {{
            setTimeout(() => {{
                const splatter = document.createElement('div');
                splatter.className = 'blood-splatter';
                
                const offsetX = (Math.random() - 0.5) * 30;
                const offsetY = Math.random() * -50;
                const dropDistance = 50 + Math.random() * 100;
                
                splatter.style.left = ({x} + offsetX) + 'px';
                splatter.style.top = ({y} + offsetY) + 'px';
                splatter.style.setProperty('--drop-distance', dropDistance + 'px');
                
                container.appendChild(splatter);
                setTimeout(() => splatter.remove(), 1000);
            }}, i * 50);
        }}
    }})();
    </script>
    """, unsafe_allow_html=True)


def show_gravity_fall(origin_x: int = None, count: int = 15):
    """显示重力下落效果"""
    start_x = origin_x if origin_x else "Math.random() * window.innerWidth"
    
    st.markdown(f"""
    <script>
    (function() {{
        const container = document.getElementById('particles-container');
        if (!container) return;
        
        const count = {count};
        const startX = {start_x};
        
        for (let i = 0; i < count; i++) {{
            setTimeout(() => {{
                const particle = document.createElement('div');
                particle.className = 'gravity-particle';
                
                const offsetX = (Math.random() - 0.5) * 100;
                const delay = Math.random() * 2;
                const duration = 1 + Math.random() * 2;
                
                particle.style.left = (startX + offsetX) + 'px';
                particle.style.top = '-10px';
                particle.style.animationDelay = delay + 's';
                particle.style.animationDuration = duration + 's';
                
                container.appendChild(particle);
                setTimeout(() => particle.remove(), (delay + duration) * 1000);
            }}, i * 100);
        }}
    }})();
    </script>
    """, unsafe_allow_html=True)


def render_glitch_text(text: str, intensity: str = 'medium'):
    """渲染故障风文字效果"""
    color_map = {'low': '#666', 'medium': '#8b0000', 'high': '#cc0000'}
    glitch_color = color_map.get(intensity, '#8b0000')
    
    st.markdown(f"""
    <style>
    .glitch-{hash(text) % 10000} {{
        position: relative;
        color: {glitch_color};
        animation: glitch 0.3s infinite;
    }}
    .glitch-{hash(text) % 10000}::before,
    .glitch-{hash(text) % 10000}::after {{
        content: '{text}';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
    }}
    .glitch-{hash(text) % 10000}::before {{
        color: #00ff00;
        animation: glitch-1 0.3s infinite;
        clip-path: polygon(0 0, 100% 0, 100% 35%, 0 35%);
    }}
    .glitch-{hash(text) % 10000}::after {{
        color: #ff0000;
        animation: glitch-2 0.3s infinite;
        clip-path: polygon(0 65%, 100% 65%, 100% 100%, 0 100%);
    }}
    @keyframes glitch-1 {{
        0%, 100% {{ transform: translate(0); }}
        20% {{ transform: translate(-2px, 0); }}
        40% {{ transform: translate(2px, 0); }}
        60% {{ transform: translate(-1px, 0); }}
        80% {{ transform: translate(1px, 0); }}
    }}
    @keyframes glitch-2 {{
        0%, 100% {{ transform: translate(0); }}
        20% {{ transform: translate(2px, 0); }}
        40% {{ transform: translate(-2px, 0); }}
        60% {{ transform: translate(1px, 0); }}
        80% {{ transform: translate(-1px, 0); }}
    }}
    </style>
    <span class="glitch-{hash(text) % 10000}">{text}</span>
    """, unsafe_allow_html=True)