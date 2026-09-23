# SVG responsivo — usa viewport responsivo
circulo_svg = """
<div style="display:flex; flex-direction:column; align-items:center; margin: 28px 0 8px 0; width: 100%;">
  <svg viewBox="0 0 1000 1000" style="width: 100%; max-width: 500px; height: auto;">
    <!-- Main circle -->
    <circle cx="500" cy="500" r="350" fill="white" stroke="#3949ab" stroke-width="5"/>
    <!-- Focus dot -->
    <circle cx="500" cy="500" r="10" fill="#1a237e"/>
  </svg>
</div>
"""
# 1. Tetraedro (4 faces)
tetraedro_svg = """
<div style="display:flex; flex-direction:column; align-items:center; margin: 28px 0 8px 0; width: 100%;">
  <svg viewBox="0 0 1000 1000" style="width: 100%; max-width: 500px; height: auto;">
    <circle cx="500" cy="500" r="420" fill="white" stroke="#e8eaf6" stroke-width="4"/>
    <polygon points="500,180 200,720 500,820" fill="#e8eaf6" opacity="0.6" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <polygon points="500,180 500,820 800,720" fill="#c5cae9" opacity="0.6" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <polygon points="200,720 500,820 800,720" fill="#9fa8da" opacity="0.6" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <line x1="500" y1="180" x2="500" y2="520" stroke="#1a237e" stroke-width="4" stroke-dasharray="10,10" opacity="0.4"/>
    <line x1="200" y1="720" x2="500" y2="520" stroke="#1a237e" stroke-width="4" stroke-dasharray="10,10" opacity="0.4"/>
    <line x1="800" y1="720" x2="500" y2="520" stroke="#1a237e" stroke-width="4" stroke-dasharray="10,10" opacity="0.4"/>
    <circle cx="500" cy="180" r="12" fill="#1a237e"/>
    <circle cx="200" cy="720" r="12" fill="#1a237e"/>
    <circle cx="800" cy="720" r="12" fill="#1a237e"/>
    <circle cx="500" cy="820" r="12" fill="#1a237e"/>
  </svg>
</div>
"""

# 2. Cubo / Hexaedro (6 faces)
cubo_svg = """
<div style="display:flex; flex-direction:column; align-items:center; margin: 28px 0 8px 0; width: 100%;">
  <svg viewBox="0 0 1000 1000" style="width: 100%; max-width: 500px; height: auto;">
    <circle cx="500" cy="500" r="420" fill="white" stroke="#e8eaf6" stroke-width="4"/>
    <polygon points="500,200 750,320 500,440 250,320" fill="#e8eaf6" opacity="0.7" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <polygon points="250,320 500,440 500,750 250,630" fill="#c5cae9" opacity="0.7" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <polygon points="500,440 750,320 750,630 500,750" fill="#9fa8da" opacity="0.7" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <line x1="250" y1="630" x2="500" y2="510" stroke="#1a237e" stroke-width="4" stroke-dasharray="10,10" opacity="0.4"/>
    <line x1="750" y1="630" x2="500" y2="510" stroke="#1a237e" stroke-width="4" stroke-dasharray="10,10" opacity="0.4"/>
    <line x1="500" y1="200" x2="500" y2="510" stroke="#1a237e" stroke-width="4" stroke-dasharray="10,10" opacity="0.4"/>
    <circle cx="500" cy="200" r="10" fill="#1a237e"/>
    <circle cx="750" cy="320" r="10" fill="#1a237e"/>
    <circle cx="250" cy="320" r="10" fill="#1a237e"/>
    <circle cx="500" cy="440" r="10" fill="#1a237e"/>
    <circle cx="250" cy="630" r="10" fill="#1a237e"/>
    <circle cx="750" cy="630" r="10" fill="#1a237e"/>
    <circle cx="500" cy="750" r="10" fill="#1a237e"/>
  </svg>
</div>
"""

# 3. Octaedro (8 faces)
octaedro_svg = """
<div style="display:flex; flex-direction:column; align-items:center; margin: 28px 0 8px 0; width: 100%;">
  <svg viewBox="0 0 1000 1000" style="width: 100%; max-width: 500px; height: auto;">
    <circle cx="500" cy="500" r="420" fill="white" stroke="#e8eaf6" stroke-width="4"/>
    <polygon points="500,150 200,500 500,600" fill="#e8eaf6" opacity="0.7" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <polygon points="500,150 500,600 800,500" fill="#c5cae9" opacity="0.7" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <polygon points="500,850 200,500 500,600" fill="#9fa8da" opacity="0.7" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <polygon points="500,850 500,600 800,500" fill="#7986cb" opacity="0.7" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <line x1="500" y1="150" x2="500" y2="400" stroke="#1a237e" stroke-width="4" stroke-dasharray="10,10" opacity="0.4"/>
    <line x1="500" y1="850" x2="500" y2="400" stroke="#1a237e" stroke-width="4" stroke-dasharray="10,10" opacity="0.4"/>
    <line x1="200" y1="500" x2="500" y2="400" stroke="#1a237e" stroke-width="4" stroke-dasharray="10,10" opacity="0.4"/>
    <line x1="800" y1="500" x2="500" y2="400" stroke="#1a237e" stroke-width="4" stroke-dasharray="10,10" opacity="0.4"/>
    <circle cx="500" cy="150" r="10" fill="#1a237e"/>
    <circle cx="200" cy="500" r="10" fill="#1a237e"/>
    <circle cx="800" cy="500" r="10" fill="#1a237e"/>
    <circle cx="500" cy="600" r="10" fill="#1a237e"/>
    <circle cx="500" cy="850" r="10" fill="#1a237e"/>
  </svg>
</div>
"""

# 4. Dodecaedro (12 faces)
dodecaedro_svg = """
<div style="display:flex; flex-direction:column; align-items:center; margin: 28px 0 8px 0; width: 100%;">
  <svg viewBox="0 0 1000 1000" style="width: 100%; max-width: 500px; height: auto;">
    <circle cx="500" cy="500" r="420" fill="white" stroke="#e8eaf6" stroke-width="4"/>
    <polygon points="500,340 642,443 588,610 412,610 358,443" fill="#e8eaf6" opacity="0.8" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <polygon points="500,340 500,170 690,232 778,400 642,443" fill="#c5cae9" opacity="0.6" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <polygon points="642,443 778,400 832,568 715,715 588,610" fill="#9fa8da" opacity="0.6" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <polygon points="588,610 715,715 500,830 285,715 412,610" fill="#7986cb" opacity="0.6" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <polygon points="412,610 285,715 168,568 222,400 358,443" fill="#9fa8da" opacity="0.6" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <polygon points="358,443 222,400 310,232 500,170 500,340" fill="#c5cae9" opacity="0.6" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <circle cx="500" cy="170" r="8" fill="#1a237e"/>
    <circle cx="690" cy="232" r="8" fill="#1a237e"/>
    <circle cx="778" cy="400" r="8" fill="#1a237e"/>
    <circle cx="832" cy="568" r="8" fill="#1a237e"/>
    <circle cx="715" cy="715" r="8" fill="#1a237e"/>
    <circle cx="500" cy="830" r="8" fill="#1a237e"/>
    <circle cx="285" cy="715" r="8" fill="#1a237e"/>
    <circle cx="168" cy="568" r="8" fill="#1a237e"/>
    <circle cx="222" cy="400" r="8" fill="#1a237e"/>
    <circle cx="310" cy="232" r="8" fill="#1a237e"/>
  </svg>
</div>
"""

# 5. Icosaedro (20 faces)
icosaedro_svg = """
<div style="display:flex; flex-direction:column; align-items:center; margin: 28px 0 8px 0; width: 100%;">
  <svg viewBox="0 0 1000 1000" style="width: 100%; max-width: 500px; height: auto;">
    <circle cx="500" cy="500" r="420" fill="white" stroke="#e8eaf6" stroke-width="4"/>
    <polygon points="500,320 680,630 320,630" fill="#e8eaf6" opacity="0.7" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <polygon points="500,320 500,160 320,630" fill="#c5cae9" opacity="0.5" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <polygon points="500,320 500,160 680,630" fill="#c5cae9" opacity="0.5" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <polygon points="500,160 210,370 320,630" fill="#9fa8da" opacity="0.5" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <polygon points="500,160 790,370 680,630" fill="#9fa8da" opacity="0.5" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <polygon points="320,630 210,370 210,680" fill="#7986cb" opacity="0.5" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <polygon points="680,630 790,370 790,680" fill="#7986cb" opacity="0.5" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <polygon points="320,630 500,840 210,680" fill="#5c6bc0" opacity="0.5" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <polygon points="680,630 500,840 790,680" fill="#5c6bc0" opacity="0.5" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <polygon points="320,630 680,630 500,840" fill="#3f51b5" opacity="0.5" stroke="#3949ab" stroke-width="6" stroke-linejoin="round"/>
    <circle cx="500" cy="160" r="9" fill="#1a237e"/>
    <circle cx="210" cy="370" r="9" fill="#1a237e"/>
    <circle cx="790" cy="370" r="9" fill="#1a237e"/>
    <circle cx="320" cy="630" r="9" fill="#1a237e"/>
    <circle cx="680" cy="630" r="9" fill="#1a237e"/>
    <circle cx="210" cy="680" r="9" fill="#1a237e"/>
    <circle cx="790" cy="680" r="9" fill="#1a237e"/>
    <circle cx="500" cy="840" r="9" fill="#1a237e"/>
    <circle cx="500" cy="320" r="9" fill="#1a237e"/>
  </svg>
</div>
"""

# Dicionário útil para iterar sobre todos os sólidos de uma vez
solidos_platonicos = {
    "tetraedro": tetraedro_svg,
    "cubo": cubo_svg,
    "octaedro": octaedro_svg,
    "dodecaedro": dodecaedro_svg,
    "icosaedro": icosaedro_svg,
    "circulo": circulo_svg
}