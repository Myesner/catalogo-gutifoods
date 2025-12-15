import os
from pdf2image import convert_from_path
try:
    from pdf2image.exceptions import PDFInfoNotInstalledError
except ImportError:
    PDFInfoNotInstalledError = Exception
from PIL import Image

# ===== CONFIGURACIÓN =====
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PDF_PATH = os.path.join(BASE_DIR, "pdf", "DELACASA CHEESE COLLECTION.pdf")
SITE_DIR = os.path.join(BASE_DIR, "docs")
PAGES_DIR = os.path.join(SITE_DIR, "pages")

DPI = 200
QUALITY = 85
# Configuración del libro
BOOK_WIDTH = 920   # Optimized for A4 double spread ratio (~1.41)
BOOK_HEIGHT = 650
PAGE_WIDTH = BOOK_WIDTH // 2
PAGE_HEIGHT = BOOK_HEIGHT
# ========================

os.makedirs(PAGES_DIR, exist_ok=True)

images = []

try:
    print("📄 Convirtiendo PDF...")
    pages = convert_from_path(PDF_PATH, dpi=DPI)
    
    for i, page in enumerate(pages):
        img = page.convert("RGB")
        name = f"page_{i+1}.jpg"
        path = os.path.join(PAGES_DIR, name)
    
        img.save(path, "JPEG", quality=QUALITY, optimize=True)
        images.append(name)
    
    print(f"✅ {len(images)} páginas creadas")

except (PDFInfoNotInstalledError, FileNotFoundError) as e:
    print(f"⚠️ No se pudo convertir el PDF (Poppler no encontrado o error): {e}")
    print("🔍 Buscando imágenes existentes en 'pages/'...")
    
    if os.path.exists(PAGES_DIR):
        files = [f for f in os.listdir(PAGES_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        # Intentar ordenar numéricamente si tienen formato page_N.jpg
        try:
            files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
        except:
            files.sort()
        images = files

    if not images:
        print("❌ ERROR CRÍTICO: No se encontraron imágenes existentes y falló la conversión del PDF.")
        print("ℹ️  Para solucionar esto, instala Poppler o coloca las imágenes manualmente en site/pages/")
        exit(1)
    else:
        print(f"✅ Usando {len(images)} imágenes existentes.")

# ===== GENERAR HTML =====
html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Catálogo GutiFoods</title>

<!-- jQuery (OBLIGATORIO primero) -->
<script src="jquery-3.7.1.min.js"></script>

<!-- Turn.js Compatibility Patch for jQuery 3+ -->
<script>
if (!$.browser) {{
  $.browser = {{}};
  (function () {{
    $.browser.msie = false;
    $.browser.version = 0;
    if (navigator.userAgent.match(/MSIE ([0-9]+)\\./)) {{
      $.browser.msie = true;
      $.browser.version = RegExp.$1;
    }}
  }})();
}}
</script>

<!-- Turn.js -->
<script src="turn.min.js"></script>

<style>
html, body {{
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  background: #333; /* Darker background like FlipHTML5 */
  overflow: hidden;
  font-family: sans-serif;
}}

/* CONTENEDOR DEL LIBRO */
#book {{
  width: {BOOK_WIDTH}px; /* Initial width */
  height: {BOOK_HEIGHT}px;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  transition: margin-left 0.2s, left 0.2s, width 0.2s, height 0.2s;
}}

.turn-page {{
  background-color: white;
  background-size: 100% 100%;
}}
.turn-page img {{
  width: 100%;
  height: 100%;
  object-fit: fill;
  pointer-events: none;
  user-select: none;
  display: block;
}}

/* Botones de navegación */
#book .shadow {{
  box-shadow: 0 4px 10px rgba(0,0,0,0.5);
}}

/* Botones de navegación */
.nav-btn {{
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 40px;
  background: rgba(0,0,0,0.5);
  color: white;
  border: none;
  cursor: pointer;
  z-index: 100;
  border-radius: 50%;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s;
}}
.nav-btn:hover {{
  background: rgba(0,0,0,0.8);
}}
.prev-btn {{ left: 20px; }}
.next-btn {{ right: 20px; }}

/* LOADING SPINNER */
#loader {{
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1000;
  border: 8px solid #f3f3f3;
  border-top: 8px solid #3498db;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  animation: spin 1s linear infinite;
}}

@keyframes spin {{
  0% {{ transform: translate(-50%, -50%) rotate(0deg); }}
  100% {{ transform: translate(-50%, -50%) rotate(360deg); }}
}}

/* CONTADOR DE PÁGINAS */
#page-counter {{
  position: fixed;
  bottom: 10px;
  right: 10px;
  left: auto;
  transform: none;
  background: rgba(0,0,0,0.4);
  color: #fff;
  padding: 5px 10px;
  border-radius: 5px;
  font-family: sans-serif;
  font-size: 12px;
  z-index: 1000;
  pointer-events: none;
}}

/* CLASE HARD (TAPA DURA) */
.hard {{
  background-color: #f0f0f0 !important;
  box-shadow: inset 0 0 5px rgba(0,0,0,0.2);
}}

/* RESPONSIVE */
@media (max-width: 600px) {{
  /* Mobile specific adjustments */
  .turn-page img {{
    object-fit: contain !important; /* Prevent distortion on mobile */
    background: #fff;
  }}
  
  .nav-btn {{
    width: 30px;
    height: 30px;
    font-size: 14px;
    background: rgba(0,0,0,0.3);
  }}
  
  .prev-btn {{ left: 5px; }}
  .next-btn {{ right: 5px; }}
  
  #page-counter {{
    font-size: 10px;
    bottom: 5px;
    right: 5px;
  }}
}}
</style>
</head>
<body>

<!-- Loader -->
<div id="loader"></div>

<!-- Contador -->
<div id="page-counter">Cargando...</div>

<!-- Botones de navegación -->
<button class="nav-btn prev-btn" id="prev">&lt;</button>
<button class="nav-btn next-btn" id="next">&gt;</button>

<div id="book">
"""

for i, img in enumerate(images):
    # Primera y última página son 'hard' (tapa dura)
    if i == 0 or i == len(images) - 1:
        css_class = "turn-page hard"
    else:
        css_class = "turn-page"
        
    html += f'  <div class="{css_class}"><img src="pages/{img}"></div>\n'

html += f"""</div>

<script>
$(document).ready(function () {{

  var aspectRatio = {BOOK_WIDTH} / {BOOK_HEIGHT};
  var isZoomed = false;

  function updateCounter(page) {{
    var total = $('#book').turn('pages');
    $('#page-counter').text('Página ' + page + ' de ' + total);
  }}

  function resizeBook() {{
    if (isZoomed) return;
    
    var winWidth = $(window).width();
    var winHeight = $(window).height();
    
    // Reduce margins significantly on mobile to maximize size
    // Increased to 20 to prevent edge cutoff
    var margin = winWidth < 600 ? 20 : 50;
    
    var availWidth = winWidth - margin;
    var availHeight = winHeight - margin;
    var newWidth, newHeight;
    
    var displayMode = availWidth < 600 ? 'single' : 'double';
    var currentAspectRatio = displayMode === 'single' ? aspectRatio / 2 : aspectRatio;
    
    if (availWidth / availHeight > currentAspectRatio) {{
      newHeight = availHeight;
      newWidth = newHeight * currentAspectRatio;
    }} else {{
      newWidth = availWidth;
      newHeight = newWidth / currentAspectRatio;
    }}
    
    $('#book').turn('size', newWidth, newHeight);
    $('#book').turn('display', displayMode);
    $('#book').turn('center');
  }}

  $('#book').turn({{
    width: {BOOK_WIDTH},
    height: {BOOK_HEIGHT},
    autoCenter: true,
    gradients: true,
    acceleration: true,
    elevation: 50,
    duration: 800,
    display: 'double',
    when: {{
      turned: function(e, page) {{
        updateCounter(page);
      }},
      start: function(e, page) {{
        $('#loader').hide();
      }}
    }}
  }});
  
  setTimeout(function(){{
    $('#loader').fadeOut();
    updateCounter(1);
  }}, 1000);

  // Keyboard
  $(document).keydown(function(e){{
    if (e.keyCode == 37) $('#book').turn('previous');
    else if (e.keyCode == 39) $('#book').turn('next');
    else if (e.keyCode == 27) {{
        if(isZoomed) toggleZoom();
    }}
  }});

  // Mouse Wheel
  var scrollTimeout;
  $(window).on('wheel', function(e) {{
    if (isZoomed) return;
    if (scrollTimeout) return;
    scrollTimeout = setTimeout(function(){{ scrollTimeout = null; }}, 250);
    if (e.originalEvent.deltaY > 0) $('#book').turn('next');
    else $('#book').turn('previous');
  }});

  // Zoom
  function toggleZoom() {{
    isZoomed = !isZoomed;
    if (isZoomed) {{
        $('#book').css({{
            'transform': 'translate(-50%, -50%) scale(1.5)',
            'z-index': '200'
        }});
        $('body').css('overflow', 'auto');
    }} else {{
        $('#book').css({{
            'transform': 'translate(-50%, -50%) scale(1)',
            'z-index': 'auto'
        }});
        $('body').css('overflow', 'hidden');
        resizeBook();
    }}
  }}

  $('#book').dblclick(function() {{
      toggleZoom();
  }});

  // Click Zones
  $('#book').on('click', function(e) {{
    if (isZoomed) return;
    var offset = $(this).offset();
    var width = $(this).width();
    var x = e.pageX - offset.left;
    if (x > width / 2) $('#book').turn('next');
    else $('#book').turn('previous');
  }});

  $('#prev').click(function() {{ $('#book').turn('previous'); }});
  $('#next').click(function() {{ $('#book').turn('next'); }});

  $(window).resize(function() {{
    resizeBook();
  }});
  
  resizeBook();

}});
</script>

</body>
</html>
"""

with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)

print("📘 Catálogo listo")
