from lxml.html import fromstring

def strip_tags(html):
    """
    htmlデータからタグ除去したテキストデータを抽出する
    ※scriptタグとstyleタグを無視
    Args:
        html: str, パースしたいhtmlデータ
    Returns:
        text: str, タグ除去されたテキストデータ
    """
    et = fromstring(html)
    xpath = r'//text()[name(..)!="script"][name(..)!="style"]'
    text = ''.join([text for text in et.xpath(xpath) if text.strip()])
    return text