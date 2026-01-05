from urllib.parse import urlparse

DOMAIN_SCORES= {
    "kmong.com": 0.2,
    "coupang.com": 0.2,
    "gmarket.co.kr": 0.2,
    "smartstore.naver.com": 0.2,
    "11st.co.kr": 0.2,
    "blog": 0.3,
    "tistory.com": 0.4,
    "namu.wiki": 0.5,
    "news.naver.com": 0.8,
    "v.daum.net": 0.8,
    "naver.com": 0.6,
    "daum.net": 0.6,
    "wikipedia.org": 0.75,
    "ko.wikipedia.org": 0.75,
    "nature.com": 0.9,
    "go.kr": 1.0,
    "gov.kr": 1.0,
    ".edu": 1.0,    
}

AD_KEYWORDS = ["/ad", ".ad", "shop", "store", "gig", "product", "buy", "sponsored", "promotion", "promo", "coupon", "discount", "sale", "order", "cart", "deal", "purchase", "hire"]

# 도메인 추출
def extract_domain(url):
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path.split('/')[0]  # netloc이 없으면 path에서 추출
    domain = domain.lower().replace("www.", "")
    return domain

# 추출한 도메인 신뢰도 점수 계산
def get_domain_score(url):
    domain = extract_domain(url)

    base_score = 0.5

    if domain in DOMAIN_SCORES:
        base_score = DOMAIN_SCORES[domain]
    else:
        for key, score in DOMAIN_SCORES.items():
            if key in domain:
                base_score = score
                break
    
    url_lower = url.lower()
    for keyword in AD_KEYWORDS:
        if keyword in url_lower:
            base_score = base_score * 0.5
            break
    return base_score

# 검증하기
if __name__ == "__main__":
    test_urls = [
        "https://www.gov.kr/portal/main",
        "https://kids.gov.kr/",
        "https://blog.naver.com/korea_gov/220793688261",
        "https://newsstand.naver.com/?pcode=0014&list=ct4",
        "https://m.blog.naver.com/healthy_foodist/223482488706",
        "https://kmong.com/gig/508399",
        "https://seo.goover.ai/report/202510/go-public-report-ko",
        "https://coupang.com/np/search?component=&q=",
        "https://smartstore.naver.com/example",
    ]

    for url in test_urls:
        domain = extract_domain(url)
        score = get_domain_score(url)
        is_ad = "광고" if score <= 0.25 else "일반"
        print(f"URL: {url} -> Domain: {domain}, Score: {score}, Type: {is_ad}")