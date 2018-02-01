def highlight(element):
    """Highlights (blinks) a Webdriver element.
    In pure javascript, as suggested by https://github.com/alp82.
    """
    driver = element._parent
    driver.execute_script("""
        element = arguments[0];
        original_style = element.getAttribute('style');
        element.setAttribute('style', original_style + "; background: yellow; border: 2px solid red;");
        setTimeout(function(){
            element.setAttribute('style', original_style);
        }, 300);
    """, element)
