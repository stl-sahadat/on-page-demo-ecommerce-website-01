import os, re, json
from bs4 import BeautifulSoup

def main():
    print("Reading base_updated.html and products data...")
    with open('base_updated.html', 'r', encoding='utf-8') as f:
        html = f.read()

    with open('js/products-data.js', 'r', encoding='utf-8') as f:
        p_text = f.read()

    m = re.search(r'window\.DESHI_MART_PRODUCTS\s*=\s*(\[.*?\]);', p_text, re.DOTALL)
    if not m:
        raise ValueError("Could not parse products data")
    products = json.loads(m.group(1))
    prod_map = {p['id']: p for p in products}

    soup = BeautifulSoup(html, 'html.parser')

    def render_card_html(p, loop_idx=1, is_carousel=False):
        pid = p['id']
        cat = p['category']
        title = p['title']
        img = p['images'][0]
        p_min = min(v['price'] for v in p['variations'])
        p_max = max(v['price'] for v in p['variations'])
        reg_min = min(v.get('regularPrice', v['price']) for v in p['variations'])
        badge_text = p.get('badge', '')
        
        if reg_min > p_min:
            price_html = f'''<span class="price"><del aria-hidden="true"><span class="woocommerce-Price-amount amount"><bdi><span class="woocommerce-Price-currencySymbol">&#2547;&nbsp;</span>{reg_min}</bdi></span></del> <ins><span class="woocommerce-Price-amount amount"><bdi><span class="woocommerce-Price-currencySymbol">&#2547;&nbsp;</span>{p_min}</bdi></span></ins></span>'''
        else:
            price_html = f'''<span class="price"><span class="woocommerce-Price-amount amount"><bdi><span class="woocommerce-Price-currencySymbol">&#2547;&nbsp;</span>{p_min}</bdi></span></span>'''

        badge_html = ''
        if badge_text:
            badge_html = f'<div class="wd-card-badge-pill">{badge_text}</div>'

        card_content = f'''<div class="wd-product wd-col wd-loop-item-814 wd-hover-parent product type-product post-{pid} status-publish instock product_cat-{cat} has-post-thumbnail shipping-taxable purchasable product-type-variable" data-loop="{loop_idx}" data-id="{pid}" data-category="{cat}">
	<div class="wd-product-wrapper wd-entry-content">
		<div class="product-card wd-custom-card-fixed">
			{badge_html}
			<div class="wd-loop-prod-thumb">
				<a href="javascript:void(0)" onclick="window.DeshiMart.openQuickView({pid}); return false;" class="wd-product-img-link" tabindex="-1" aria-label="{title}">
					<img loading="lazy" decoding="async" src="{img}" alt="{title}" />
				</a>
			</div>
			<div class="wd-card-body">
				<div class="wd-loop-prod-title">
					<h3><a href="javascript:void(0)" onclick="window.DeshiMart.openQuickView({pid}); return false;">{title}</a></h3>
				</div>
				<div class="wd-loop-prod-price">
					{price_html}
				</div>
				<div class="product-card-btn-row">
					<a href="javascript:void(0)" onclick="window.DeshiMart.addProductToCartFromCard({pid}, this); return false;" class="button product_type_variable add_to_cart_button" aria-label="Add to cart" tabindex="-1"><span>অ্যাড টু কার্ট</span></a>
					<a href="javascript:void(0)" onclick="window.DeshiMart.quickBuyNow({pid}); return false;" class="button product_type_variable isl-loop-buy-now" aria-label="Buy now" tabindex="-1"><span>অর্ডার করুন</span></a>
				</div>
			</div>
		</div>
	</div>
</div>'''
        if is_carousel:
            return f'<div class="wd-carousel-item">{card_content}</div>'
        return card_content

    # 1. Update logo links to stay on page
    for logo_link in soup.find_all('a', class_='wd-logo'):
        logo_link['href'] = '#'
        logo_link['onclick'] = 'window.scrollTo({top:0, behavior:"smooth"}); return false;'

    # 2. Update header cart & mobile toolbar cart
    for cart_el in soup.find_all(['div', 'a'], class_=['wd-header-cart', 'wd-toolbar-cart', 'cart-widget-opener']):
        cart_el['onclick'] = 'window.DeshiMart.openCartDrawer(); return false;'
        cart_el['style'] = 'cursor: pointer;'
        a = cart_el if cart_el.name == 'a' else cart_el.find('a')
        if a:
            a['href'] = 'javascript:void(0)'
            a['onclick'] = 'window.DeshiMart.openCartDrawer(); return false;'

    # 2b. Update side cart close button
    for close_btn in soup.find_all('div', class_='close-side-widget'):
        a = close_btn.find('a')
        if a:
            a['href'] = 'javascript:void(0)'
            a['onclick'] = 'window.DeshiMart.closeCartDrawer(); return false;'

    # 3. Update mobile toolbar shop
    for shop_el in soup.find_all('div', class_='wd-toolbar-shop'):
        a = shop_el.find('a')
        if a:
            a['href'] = '#'
            a['onclick'] = 'window.scrollTo({top:0, behavior:"smooth"}); return false;'

    # 4. Top menu items: rebuild in exact sequential vertical on-page order!
    # Sequence: 1. Ghee -> 2. Oil -> 3. Honey & Dates -> 4. Tea -> 5. Nuts -> 6. Spices -> 7. Shutki -> 8. All Products
    nav_definitions = [
        ('ghee', 'Ghee', 'গাওয়া ঘি'),
        ('oil', 'Oil', 'খাঁটি তেল'),
        ('honey', 'Honey & Dates', 'মধু ও খেজুর'),
        ('tea', 'Tea', 'চা পাতা'),
        ('nuts', 'Nuts', 'বাদাম ও বীজ'),
        ('spices', 'Spices', 'মসলা'),
        ('shutki', 'Shutki', 'শুঁটকি'),
        ('all', 'All Products', 'সব পণ্য'),
    ]

    for menu_id in ['menu-products-menu', 'menu-products-menu-1']:
        menu_el = soup.find('ul', id=menu_id)
        if menu_el:
            menu_el.clear()
            for slug, label, b_label in nav_definitions:
                li = soup.new_tag('li', id=f'{menu_id}-{slug}', **{'class': 'menu-item menu-item-type-taxonomy menu-item-object-product_cat item-level-0 menu-simple-dropdown wd-event-hover'})
                a = soup.new_tag('a', href='javascript:void(0)', onclick=f"window.DeshiMart.scrollToCategory('{slug}'); return false;", **{'class': 'woodmart-nav-link'})
                span = soup.new_tag('span', **{'class': 'nav-link-text'})
                span.string = label
                a.append(span)
                li.append(a)
                menu_el.append(li)

    # 5. Update all category links (nav, grid, carousel)
    for a in soup.find_all('a'):
        href = a.get('href', '')
        if 'category/' in href:
            slug = href.strip('/').split('/')[-1]
            a['href'] = 'javascript:void(0)'
            a['onclick'] = f"window.DeshiMart.scrollToCategory('{slug}'); return false;"
        elif 'demo7.itservicelab.com' in href and not any(s in href for s in ['facebook.com', 'x.com', 'linkedin.com', 'telegram.me', 'pinterest.com']):
            a['href'] = 'javascript:void(0)'

    # 6. Realign Homepage Sections:
    # 6a. Section 'All Homemade Ghee' -> render clean cards
    for h in soup.find_all('h2', class_='elementor-heading-title'):
        if 'All Homemade Ghee' in h.get_text():
            parent = h.find_parent('div', class_='elementor-element')
            while parent and not parent.find(class_='wd-carousel-wrap'):
                parent = parent.parent
            if parent:
                c_wrap = parent.find(class_='wd-carousel-wrap')
                if c_wrap:
                    c_wrap.clear()
                    ghee_ids = [533, 534, 532, 531, 446, 535, 463]
                    for idx, pid in enumerate(ghee_ids, 1):
                        if pid in prod_map:
                            c_card = BeautifulSoup(render_card_html(prod_map[pid], idx, is_carousel=True), 'html.parser')
                            c_wrap.append(c_card)

        # 6b. Section 'All Honey/Dates' -> Purely Honey & Dates products!
        elif 'All Honey/Dates' in h.get_text():
            parent = h.find_parent('div', class_='elementor-element')
            while parent and not parent.find(class_='wd-carousel-wrap'):
                parent = parent.parent
            if parent:
                c_wrap = parent.find(class_='wd-carousel-wrap')
                if c_wrap:
                    c_wrap.clear()
                    honey_dates_ids = [530, 536, 528, 537, 527, 529]
                    for idx, pid in enumerate(honey_dates_ids, 1):
                        if pid in prod_map:
                            c_card = BeautifulSoup(render_card_html(prod_map[pid], idx, is_carousel=True), 'html.parser')
                            c_wrap.append(c_card)

        # 6c. Section 'All Exclusive Products' -> Pure Oils & Exclusive Items!
        elif 'All Exclusive Products' in h.get_text():
            parent = h.find_parent('div', class_='elementor-element')
            while parent and not parent.find(class_='wd-carousel-wrap'):
                parent = parent.parent
            if parent:
                c_wrap = parent.find(class_='wd-carousel-wrap')
                if c_wrap:
                    c_wrap.clear()
                    exclusive_ids = [538, 453, 450, 541, 542, 543, 459]
                    for idx, pid in enumerate(exclusive_ids, 1):
                        if pid in prod_map:
                            c_card = BeautifulSoup(render_card_html(prod_map[pid], idx, is_carousel=True), 'html.parser')
                            c_wrap.append(c_card)

        # 6d. Section 'All Products' -> Add Category Filter Bar and all 25 Products!
        elif 'All Products' in h.get_text():
            parent = h.find_parent('div', class_='elementor-element')
            while parent and not parent.find(class_='products'):
                parent = parent.parent
            if parent:
                p_grid = parent.find(class_='products')
                if p_grid:
                    filter_nav_html = '''
<div class="wd-category-filter-wrap" style="width:100%; margin-bottom:25px;">
  <ul class="wd-category-filter-nav">
    <li><button type="button" class="wd-category-filter-btn active" data-cat="all" onclick="window.DeshiMart.filterCategory('all', this); return false;">সব পণ্য</button></li>
    <li><button type="button" class="wd-category-filter-btn" data-cat="ghee" onclick="window.DeshiMart.filterCategory('ghee', this); return false;">গাওয়া ঘি</button></li>
    <li><button type="button" class="wd-category-filter-btn" data-cat="oil" onclick="window.DeshiMart.filterCategory('oil', this); return false;">খাঁটি তেল</button></li>
    <li><button type="button" class="wd-category-filter-btn" data-cat="honey" onclick="window.DeshiMart.filterCategory('honey', this); return false;">খাঁটি মধু</button></li>
    <li><button type="button" class="wd-category-filter-btn" data-cat="dates" onclick="window.DeshiMart.filterCategory('dates', this); return false;">খেজুর</button></li>
    <li><button type="button" class="wd-category-filter-btn" data-cat="tea" onclick="window.DeshiMart.filterCategory('tea', this); return false;">চা পাতা</button></li>
    <li><button type="button" class="wd-category-filter-btn" data-cat="nuts" onclick="window.DeshiMart.filterCategory('nuts', this); return false;">বাদাম ও বীজ</button></li>
    <li><button type="button" class="wd-category-filter-btn" data-cat="spices" onclick="window.DeshiMart.filterCategory('spices', this); return false;">মসলা</button></li>
    <li><button type="button" class="wd-category-filter-btn" data-cat="shutki" onclick="window.DeshiMart.filterCategory('shutki', this); return false;">শুঁটকি</button></li>
  </ul>
</div>
'''
                    filter_soup = BeautifulSoup(filter_nav_html, 'html.parser')
                    p_grid.insert_before(filter_soup)

                    p_grid.clear()
                    ordered_ids = [
                        533, 538, 530, 528, 459, 541, 543, 545,
                        534, 453, 536, 537, 458, 542, 544, 546,
                        532, 450, 527, 529, 540, 531, 446, 535, 463
                    ]
                    for idx, pid in enumerate(ordered_ids, 1):
                        if pid in prod_map:
                            grid_card = BeautifulSoup(render_card_html(prod_map[pid], idx, is_carousel=False), 'html.parser')
                            p_grid.append(grid_card)

        # 6e. Section 'Top Selling Products' -> Render clean 4-column cards (no awkward empty whitespace!)
        elif 'Top Selling Products' in h.get_text():
            parent = h.find_parent('div', class_='elementor-element')
            while parent and not parent.find(class_='products'):
                parent = parent.parent
            if parent:
                p_grid = parent.find(class_='products')
                if p_grid:
                    p_grid['class'] = [c for c in p_grid.get('class', []) if c != 'grid-columns-2'] + ['grid-columns-4', 'wd-top-selling-grid']
                    p_grid['style'] = '--wd-col-lg:4;--wd-col-md:3;--wd-col-sm:2;--wd-gap-lg:20px;--wd-gap-sm:10px;'
                    p_grid.clear()
                    top_selling_ids = [533, 530, 534, 532]
                    for idx, pid in enumerate(top_selling_ids, 1):
                        if pid in prod_map:
                            grid_card = BeautifulSoup(render_card_html(prod_map[pid], idx, is_carousel=False), 'html.parser')
                            p_grid.append(grid_card)

    # 7. Bind real product handlers to all cards
    cards = soup.find_all(class_='wd-product')
    for card in cards:
        pid = card.get('data-id')
        if not pid:
            continue
        int_pid = int(pid) if pid.isdigit() else 0
        if int_pid in prod_map:
            card['data-category'] = prod_map[int_pid]['category']

        # Image link
        img_link = card.find('a', class_='wd-product-img-link')
        if img_link:
            img_link['href'] = 'javascript:void(0)'
            img_link['onclick'] = f'window.DeshiMart.openQuickView({pid}); return false;'

        # Quick view link
        qv_link = card.find('a', class_='open-quick-view')
        if qv_link:
            qv_link['href'] = 'javascript:void(0)'
            qv_link['onclick'] = f'window.DeshiMart.openQuickView({pid}); return false;'

        # Title link
        title_wrap = card.find(class_='wd-loop-prod-title')
        if title_wrap:
            t_link = title_wrap.find('a')
            if t_link:
                t_link['href'] = 'javascript:void(0)'
                t_link['onclick'] = f'window.DeshiMart.openQuickView({pid}); return false;'

        # Select options / Add to Cart button
        btn = card.find('a', class_='add_to_cart_button')
        if btn:
            btn['href'] = 'javascript:void(0)'
            btn['onclick'] = f'window.DeshiMart.addProductToCartFromCard({pid}, this); return false;'

        # Buy Now button
        buy_btn = card.find('a', class_='isl-loop-buy-now')
        if buy_btn:
            buy_btn['href'] = 'javascript:void(0)'
            buy_btn['onclick'] = f'window.DeshiMart.quickBuyNow({pid}); return false;'

    # 7b. Decompose old buggy WoodMart toolbar
    for tb in soup.find_all('div', class_='wd-toolbar'):
        tb.decompose()

    # 8. Ensure woodmart-loaded class on all slides so backgrounds appear immediately
    for slide in soup.find_all(class_='wd-slide'):
        classes = slide.get('class', [])
        if 'woodmart-loaded' not in classes:
            classes.append('woodmart-loaded')
            slide['class'] = classes

    # 8b. Performance Optimization 1: Consolidate ALL 150+ separate CSS files into 1 high-speed bundle
    links = soup.find_all('link', rel=lambda r: r and 'stylesheet' in r)
    combined_css = []
    first_link = None
    for l in links:
        href = l.get('href', '').split('?')[0].lstrip('./')
        if os.path.exists(href) and not href.startswith(('http:', 'https:')) and href != 'css/bundle.min.css':
            with open(href, 'r', encoding='utf-8', errors='ignore') as fp:
                css_text = fp.read()
            combined_css.append(f'/* {href} */\n' + css_text)
            if first_link is None:
                first_link = l
            else:
                l.decompose()

    # Also extract styles from inside template tags (like template 921 and 1010)
    for tmpl in soup.find_all('template'):
        for l in tmpl.find_all('link', rel=lambda r: r and 'stylesheet' in r):
            href = l.get('href', '').split('?')[0].lstrip('./')
            if os.path.exists(href) and not href.startswith(('http:', 'https:')):
                with open(href, 'r', encoding='utf-8', errors='ignore') as fp:
                    combined_css.append(f'/* {href} */\n' + fp.read())
                l.decompose()

    if combined_css and first_link:
        os.makedirs('css', exist_ok=True)
        with open('css/bundle.min.css', 'w', encoding='utf-8') as fp:
            fp.write('\n'.join(combined_css))
        first_link['href'] = 'css/bundle.min.css'
        first_link['id'] = 'woodmart-bundle-css'

    # Deduplicate any remaining external links
    seen_hrefs = set()
    for l in soup.find_all('link', rel=lambda r: r and 'stylesheet' in r):
        href = l.get('href')
        if href in seen_hrefs:
            l.decompose()
        else:
            seen_hrefs.add(href)

    # 8c. Performance Optimization 2: Defer all scripts to prevent render-blocking
    for s in soup.find_all('script', src=True):
        s['defer'] = ''

    # 8d. Performance Optimization 3: Add lazy-loading and async decoding to images
    for img_tag in soup.find_all('img'):
        if 'loading' not in img_tag.attrs:
            img_tag['loading'] = 'lazy'
        if 'decoding' not in img_tag.attrs:
            img_tag['decoding'] = 'async'

    html = str(soup)

    # 9. Slide backgrounds, Cart Badge & Button Layout Overrides in head
    extra_slide_style = '''
<style id="custom-slide-bg-css">
/* Authentic WoodMart Slide Backgrounds */
#slide-106 .wd-slide-bg, #slide-106.woodmart-loaded .wd-slide-bg { background-image:url(./wp-content/uploads/2026/08/banner-4.webp) !important; background-size:cover !important; background-position:center !important; }
#slide-110 .wd-slide-bg, #slide-110.woodmart-loaded .wd-slide-bg { background-image:url(./wp-content/uploads/2026/08/banner-3.webp) !important; background-size:cover !important; background-position:center !important; }
#slide-111 .wd-slide-bg, #slide-111.woodmart-loaded .wd-slide-bg { background-image:url(./wp-content/uploads/2026/08/banner-2.webp) !important; background-size:cover !important; background-position:center !important; }
#slide-361 .wd-slide-bg, #slide-361.woodmart-loaded .wd-slide-bg { background-image:url(./wp-content/uploads/2026/08/banner-1.webp) !important; background-size:cover !important; background-position:center !important; }

/* Pixel Perfect Cart Icon Badge - Matching User Image */
.wd-header-cart .wd-tools-count, 
.whb-col-right .wd-cart-number, 
.wd-toolbar-cart .wd-tools-count {
  position: absolute !important;
  top: -6px !important;
  right: -8px !important;
  background-color: #f57224 !important;
  color: #ffffff !important;
  border-radius: 50% !important;
  min-width: 18px !important;
  height: 18px !important;
  padding: 0 4px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  font-size: 11px !important;
  font-weight: 700 !important;
  line-height: 1 !important;
  box-shadow: 0 2px 5px rgba(245, 114, 36, 0.4) !important;
  z-index: 5 !important;
  transition: transform 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
}

/* Sticky Header Fix - Completely eliminates the 105px empty whiteboard */
header.whb-header.whb-sticked {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  z-index: 1000 !important;
  padding: 0 !important;
  margin: 0 !important;
  height: 48px !important;
  min-height: 48px !important;
  max-height: 48px !important;
  background: transparent !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15) !important;
  animation: wdSlideDown 0.3s ease !important;
}

header.whb-header.whb-sticked .whb-general-header,
header.whb-header.whb-sticked .whb-top-bar {
  display: none !important;
}

header.whb-header.whb-sticked .whb-main-header {
  height: 48px !important;
  min-height: 48px !important;
  max-height: 48px !important;
  position: static !important;
  box-shadow: none !important;
  background: transparent !important;
}

header.whb-header.whb-sticked .whb-header-bottom {
  height: 48px !important;
  min-height: 48px !important;
  max-height: 48px !important;
  background: #111827 !important;
}

header.whb-header.whb-sticked .whb-header-bottom .whb-flex-row {
  height: 48px !important;
  min-height: 48px !important;
  max-height: 48px !important;
}

[id],
.elementor-element {
  scroll-margin-top: 58px !important;
}


/* =========================================================
   DESKTOP STICKY NAVBAR WITH LOGO
   ========================================================= */
#dm-sticky-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10000;
  background: #ffffff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border-bottom: 1px solid #f1f5f9;
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.25s ease;
  transform: translateY(-100%);
  opacity: 0;
  pointer-events: none;
  display: block;
}
#dm-sticky-navbar.is-visible {
  transform: translateY(0);
  opacity: 1;
  pointer-events: auto;
}
.dm-sticky-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 20px;
  height: 58px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.dm-sticky-logo img {
  height: 38px;
  width: auto;
  display: block;
}
.dm-sticky-nav-links {
  display: flex;
  align-items: center;
  gap: 16px;
}
.dm-sticky-nav-links a {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  text-decoration: none;
  padding: 6px 4px;
  transition: color 0.2s ease;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.dm-sticky-nav-links a:hover {
  color: #f57224;
}
.dm-sticky-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
.dm-sticky-cart-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  cursor: pointer;
  color: #1e293b;
  transition: all 0.2s ease;
}
.dm-sticky-cart-btn:hover {
  background: #fff7ed;
  border-color: #fdba74;
  color: #ea580c;
}
.dm-sticky-cart-count {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #f57224;
  color: #ffffff;
  font-size: 10px;
  font-weight: 700;
  width: 17px;
  height: 17px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}
.dm-sticky-order-cta {
  background: #f57224;
  color: #ffffff;
  border: none;
  padding: 8px 18px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.15s ease;
}
.dm-sticky-order-cta:hover {
  background: #d85a14;
  transform: translateY(-1px);
}

/* =========================================================
   MOBILE STICKY HEADER WITH LOGO
   ========================================================= */
#dm-mobile-sticky-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 52px;
  background: #ffffff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  border-bottom: 1px solid #f1f5f9;
  z-index: 10000;
  display: none;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.25s ease;
  transform: translateY(-100%);
  opacity: 0;
  pointer-events: none;
}
#dm-mobile-sticky-header.is-visible {
  transform: translateY(0);
  opacity: 1;
  pointer-events: auto;
}
.dm-mob-logo img {
  height: 32px;
  width: auto;
  display: block;
}
.dm-mob-icon-btn {
  color: #1e293b !important;
  background: #f8fafc !important;
  border: 1px solid #e2e8f0 !important;
  outline: none;
}
.dm-mob-icon-btn svg {
  stroke: #1e293b !important;
  display: block !important;
  margin: auto !important;
}
.dm-mob-icon-btn
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #1e293b;
  position: relative;
  cursor: pointer;
}
.dm-mob-cart-badge {
  position: absolute;
  top: -3px;
  right: -3px;
  background: #f57224;
  color: #ffffff;
  font-size: 10px;
  font-weight: 700;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

/* =========================================================
   MODERN MOBILE BOTTOM NAVIGATION BAR
   ========================================================= */
#dm-mobile-bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 58px;
  background: #ffffff;
  border-top: 1px solid #e2e8f0;
  box-shadow: 0 -4px 15px rgba(0, 0, 0, 0.05);
  z-index: 99999;
  display: none;
  align-items: center;
  justify-content: space-around;
  padding: 0 4px;
  padding-bottom: env(safe-area-inset-bottom, 0px);
  box-sizing: border-box;
}
.dm-bottom-nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  text-decoration: none;
  color: #64748b;
  font-size: 10px;
  font-weight: 600;
  cursor: pointer;
  position: relative;
  padding: 5px 0;
  transition: color 0.2s ease;
}
.dm-bottom-nav-item svg {
  width: 20px;
  height: 20px;
}
.dm-bottom-nav-item:hover, .dm-bottom-nav-item.active {
  color: #f57224;
}
.dm-bottom-cart-badge {
  position: absolute;
  top: 2px;
  right: calc(50% - 15px);
  background: #f57224;
  color: #ffffff;
  font-size: 9px;
  font-weight: 700;
  width: 15px;
  height: 15px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

/* Hide old buggy WoodMart toolbar */
.wd-toolbar {
  display: none !important;
}

/* Media Query Responsive Visibility */
@media (max-width: 1024px) {
  #dm-sticky-navbar {
    display: none !important;
  }
  #dm-mobile-sticky-header {
    display: flex;
  }
  #dm-mobile-bottom-nav {
    display: flex;
  }
  body {
    padding-bottom: 72px !important;
  }
}
@media (min-width: 1025px) {
  #dm-mobile-sticky-header {
    display: none !important;
  }
  #dm-mobile-bottom-nav {
    display: none !important;
  }
}

/* Cart Badge Bounce Animation */
.wd-cart-badge-bounce {
  animation: wdBadgeBounce 0.45s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
}
@keyframes wdBadgeBounce {
  0% { transform: scale(1); }
  40% { transform: scale(1.45); }
  100% { transform: scale(1); }
}

/* Category Filter Navigation Bar */
.wd-category-filter-nav {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin: 15px 0 25px 0;
  padding: 0;
  list-style: none;
}
.wd-category-filter-btn {
  display: inline-block;
  padding: 8px 18px;
  font-size: 13px;
  font-weight: 600;
  color: #444;
  background: #f8f9fa;
  border: 1px solid #e2e8f0;
  border-radius: 24px;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
  font-family: inherit;
}
.wd-category-filter-btn:hover {
  color: var(--wd-primary-color, #78a206);
  border-color: var(--wd-primary-color, #78a206);
  background: #ffffff;
  transform: translateY(-1px);
}
.wd-category-filter-btn.active {
  color: #ffffff !important;
  background-color: var(--wd-primary-color, #78a206) !important;
  border-color: var(--wd-primary-color, #78a206) !important;
  box-shadow: 0 3px 8px rgba(120, 162, 6, 0.3) !important;
}

/* Smooth Category Filter Card Animations */
.wd-product.wd-cat-hidden {
  display: none !important;
}
.wd-product.wd-cat-visible {
  animation: wdFadeInUp 0.35s ease forwards;
}
@keyframes wdFadeInUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ========================================================
   FIX 1: DISCOUNT BADGE ALWAYS VISIBLE ON HOVER & QUICKVIEW
======================================================== */
.wd-pd-main-image-wrap {
  position: relative !important;
  overflow: hidden !important;
}
.wd-pd-discount-badge {
  position: absolute !important;
  top: 14px !important;
  left: 14px !important;
  background: #ef4444 !important;
  color: #ffffff !important;
  font-size: 13px !important;
  font-weight: 700 !important;
  padding: 4px 10px !important;
  border-radius: 5px !important;
  box-shadow: 0 3px 8px rgba(239, 68, 68, 0.4) !important;
  z-index: 999 !important;
  pointer-events: none !important;
  display: inline-block !important;
}
.wd-pd-main-image {
  position: relative !important;
  z-index: 1 !important;
  transition: transform 0.35s ease !important;
}
.wd-pd-main-image:hover,
.wd-pd-main-image-wrap:hover .wd-pd-main-image {
  transform: scale(1.06) !important;
}

.wd-product .wp-block-wd-icon,
.wd-product .product-labels,
.wd-product .onsale {
  position: relative !important;
  z-index: 20 !important;
  pointer-events: none !important;
}

/* ========================================================
   FIX 2: BUTTON OVERFLOW FIX - 100% CONTAINER CONFINED
======================================================== */
.product-card-btn-row,
.wd-product .product-card-btn-row,
.wd-product .wd-90eb1c9a,
.wd-product .wd-39fb7563 {
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  justify-content: space-between !important;
  gap: 6px !important;
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box !important;
  margin-top: 10px !important;
  padding: 0 !important;
}

.product-card-btn-row > a,
.wd-product .product-card-btn-row > a,
.wd-product .add_to_cart_button,
.wd-product .isl-loop-buy-now {
  flex: 1 1 50% !important;
  width: 50% !important;
  max-width: 50% !important;
  min-width: 0 !important;
  height: 35px !important;
  min-height: 35px !important;
  max-height: 35px !important;
  padding: 0 4px !important;
  margin: 0 !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  line-height: 33px !important;
  border-radius: 5px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  text-align: center !important;
  white-space: nowrap !important;
  box-sizing: border-box !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  cursor: pointer !important;
  text-decoration: none !important;
}

.wd-product .add_to_cart_button {
  background: #ffffff !important;
  color: #f47b20 !important;
  border: 1.5px solid #f47b20 !important;
}
.wd-product .add_to_cart_button:hover {
  background: #f47b20 !important;
  color: #ffffff !important;
}

.wd-product .isl-loop-buy-now {
  background: #f47b20 !important;
  color: #ffffff !important;
  border: 1.5px solid #f47b20 !important;
}
.wd-product .isl-loop-buy-now:hover {
  background: #111827 !important;
  border-color: #111827 !important;
  color: #ffffff !important;
}

/* Remove bulky pseudo-icon that caused text to spill out */
.isl-loop-buy-now::before {
  display: none !important;
  content: "" !important;
}

/* ========================================================
   FIX 3: PIXEL-PERFECT EQUAL CARD HEIGHTS & STRAIGHT BUTTON LINE
======================================================== */
.wd-carousel-wrap {
  display: flex !important;
  align-items: stretch !important;
}
.wd-carousel-item {
  height: auto !important;
  display: flex !important;
  flex-direction: column !important;
}
.wd-product.wd-col,
.wd-product {
  height: 100% !important;
  display: flex !important;
  flex-direction: column !important;
}
.wd-product-wrapper {
  height: 100% !important;
  display: flex !important;
  flex-direction: column !important;
  flex: 1 1 auto !important;
}
.product-card.wd-custom-card-fixed,
.product-card {
  height: 100% !important;
  min-height: 330px !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: space-between !important;
  position: relative !important;
  background: #ffffff !important;
  border: 1px solid #ffe4d1 !important;
  border-radius: 8px !important;
  padding: 12px 10px 12px 10px !important;
  box-sizing: border-box !important;
  transition: all 0.25s ease !important;
}
.product-card.wd-custom-card-fixed:hover,
.product-card:hover {
  border-color: #f47b20 !important;
  box-shadow: 0 8px 24px rgba(244, 123, 32, 0.12) !important;
  transform: translateY(-2px) !important;
}

/* Badge Pill - Absolute, never offsets content flow */
.wd-card-badge-pill {
  position: absolute !important;
  top: 10px !important;
  left: 10px !important;
  background: #f47b20 !important;
  color: #ffffff !important;
  font-size: 11px !important;
  font-weight: 700 !important;
  padding: 3px 8px !important;
  border-radius: 4px !important;
  z-index: 5 !important;
  pointer-events: none !important;
  line-height: 1.2 !important;
  box-shadow: 0 2px 4px rgba(244, 123, 32, 0.3) !important;
}

/* Hide unstyled / displaced Quick view text in card loops */
.wd-loop-prod-actions,
.wd-product .quick-view.wd-action-btn,
.wd-product .wd-quick-view-btn {
  display: none !important;
}

/* Thumbnail Box: Fixed Height, Perfectly Centered */
.wd-loop-prod-thumb {
  width: 100% !important;
  height: 180px !important;
  min-height: 180px !important;
  max-height: 180px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  margin: 0 0 10px 0 !important;
  padding: 4px !important;
  box-sizing: border-box !important;
  position: relative !important;
  overflow: hidden !important;
}
.wd-loop-prod-thumb a.wd-product-img-link {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 100% !important;
  height: 100% !important;
}
.wd-loop-prod-thumb img {
  max-height: 165px !important;
  max-width: 100% !important;
  width: auto !important;
  height: auto !important;
  object-fit: contain !important;
  display: block !important;
  margin: 0 auto !important;
  transition: transform 0.3s ease !important;
}
.product-card:hover .wd-loop-prod-thumb img {
  transform: scale(1.05) !important;
}

/* Card Body: Flex Column, Pushes Buttons to Bottom */
.wd-card-body {
  display: flex !important;
  flex-direction: column !important;
  flex: 1 1 auto !important;
  justify-content: space-between !important;
  width: 100% !important;
}

/* Title: Fixed 2-Line Box */
.wd-loop-prod-title {
  height: 38px !important;
  min-height: 38px !important;
  max-height: 38px !important;
  margin: 0 0 6px 0 !important;
  overflow: hidden !important;
  text-align: center !important;
}
.wd-loop-prod-title h3,
.wd-loop-prod-title h3 a {
  font-size: 13px !important;
  line-height: 1.35 !important;
  font-weight: 600 !important;
  color: #1e293b !important;
  display: -webkit-box !important;
  -webkit-line-clamp: 2 !important;
  -webkit-box-orient: vertical !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  text-decoration: none !important;
  margin: 0 !important;
  padding: 0 !important;
}
.wd-loop-prod-title h3 a:hover {
  color: #f47b20 !important;
}

/* Price: Fixed Height */
.wd-loop-prod-price {
  height: 24px !important;
  min-height: 24px !important;
  max-height: 24px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  margin: 0 0 10px 0 !important;
  font-size: 13px !important;
  text-align: center !important;
}
.wd-loop-prod-price .price {
  display: inline-flex !important;
  align-items: baseline !important;
  gap: 6px !important;
}
.wd-loop-prod-price del {
  color: #94a3b8 !important;
  font-size: 11px !important;
}
.wd-loop-prod-price ins, 
.wd-loop-prod-price .amount {
  color: #f47b20 !important;
  font-weight: 700 !important;
  text-decoration: none !important;
}

/* ========================================================
   TOP SELLING PRODUCTS GRID - 4 COLUMNS (NO EMPTY VOID)
======================================================== */
.elementor-element-1fc9550 {
  margin-top: 40px !important;
  margin-bottom: 30px !important;
}

.elementor-element-57a3ae0 {
  margin-bottom: 24px !important;
  text-align: center !important;
}
.elementor-element-57a3ae0 .elementor-heading-title {
  text-align: center !important;
  font-size: 22px !important;
  font-weight: 700 !important;
  color: #1e293b !important;
  position: relative !important;
  display: inline-block !important;
  padding-bottom: 8px !important;
}
.elementor-element-57a3ae0 .elementor-heading-title::after {
  content: "" !important;
  position: absolute !important;
  bottom: 0 !important;
  left: 50% !important;
  transform: translateX(-50%) !important;
  width: 48px !important;
  height: 3px !important;
  background-color: #f47b20 !important;
  border-radius: 2px !important;
}

.wd-top-selling-grid {
  display: grid !important;
  grid-template-columns: repeat(4, 1fr) !important;
  gap: 16px !important;
  width: 100% !important;
  box-sizing: border-box !important;
}

@media (max-width: 1024px) {
  .wd-top-selling-grid {
    grid-template-columns: repeat(3, 1fr) !important;
    gap: 12px !important;
  }
}

/* ========================================================
   FIX 4: MOBILE RESPONSIVE (MAX-WIDTH: 768PX)
======================================================== */
@media (max-width: 768px) {
  .wd-top-selling-grid {
    grid-template-columns: repeat(2, 1fr) !important;
    gap: 8px !important;
  }
  /* Exactly 2 products per row in carousels */
  .wd-carousel-container,
  .wd-carousel-inner,
  .wd-carousel {
    width: 100% !important;
    max-width: 100% !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
  }
  .wd-carousel-wrap {
    width: 100% !important;
    max-width: 100% !important;
    transform: none !important;
    display: flex !important;
    overflow-x: auto !important;
    scroll-snap-type: x mandatory !important;
    -webkit-overflow-scrolling: touch !important;
    margin: 0 !important;
    padding: 0 4px !important;
    gap: 8px !important;
    box-sizing: border-box !important;
  }
  .wd-carousel-item {
    flex: 0 0 calc(50% - 4px) !important;
    max-width: calc(50% - 4px) !important;
    width: calc(50% - 4px) !important;
    min-width: calc(50% - 4px) !important;
    box-sizing: border-box !important;
    padding: 0 !important;
    scroll-snap-align: start !important;
    display: flex !important;
  }

  /* Hide intrusive arrows on mobile touch swipe */
  .wd-nav-arrows {
    display: none !important;
  }

  /* Exactly 2 products per row in grids (target only the grid, never the carousels) */
  .products.elements-grid,
  .products:not(.wd-carousel-container):not(.wd-carousel-wrap):not(.wd-carousel) {
    display: grid !important;
    grid-template-columns: repeat(2, 1fr) !important;
    gap: 8px !important;
    padding: 0 4px !important;
  }
  .wd-product.wd-col {
    width: 100% !important;
    max-width: 100% !important;
    flex: 0 0 100% !important;
  }
  .product-card.wd-custom-card-fixed,
  .product-card {
    min-height: 285px !important;
    padding: 8px 6px 8px 6px !important;
  }
  .wd-loop-prod-thumb {
    height: 125px !important;
    min-height: 125px !important;
    max-height: 125px !important;
    margin-bottom: 6px !important;
  }
  .wd-loop-prod-thumb img {
    max-height: 115px !important;
  }
  .wd-loop-prod-title {
    height: 32px !important;
    min-height: 32px !important;
    max-height: 32px !important;
    margin-bottom: 4px !important;
  }
  .wd-loop-prod-title h3,
  .wd-loop-prod-title h3 a {
    font-size: 11px !important;
    line-height: 1.25 !important;
  }
  .wd-loop-prod-price {
    height: 18px !important;
    min-height: 18px !important;
    max-height: 18px !important;
    font-size: 11px !important;
    margin-bottom: 6px !important;
  }
  .product-card-btn-row,
  .wd-product .product-card-btn-row {
    display: flex !important;
    flex-direction: column !important;
    gap: 5px !important;
    width: 100% !important;
    max-width: 100% !important;
    margin-top: 6px !important;
  }
  .product-card-btn-row > a,
  .wd-product .product-card-btn-row > a,
  .wd-product .add_to_cart_button,
  .wd-product .isl-loop-buy-now {
    width: 100% !important;
    max-width: 100% !important;
    flex: 1 1 100% !important;
    height: 28px !important;
    min-height: 28px !important;
    max-height: 28px !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    line-height: 26px !important;
    padding: 0 4px !important;
    border-radius: 4px !important;
    box-sizing: border-box !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    text-align: center !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
  }
  .product-card-btn-row > a > span {
    display: inline-block !important;
    max-width: 100% !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
    font-size: 11px !important;
    line-height: 1 !important;
  }
  .wd-card-badge-pill {
    font-size: 9px !important;
    padding: 2px 5px !important;
    top: 6px !important;
    left: 6px !important;
  }
}
</style>
'''
    html = html.replace('</head>', extra_slide_style + '\n</head>')

    # 10. Load template_921.html and template_1010.html
    with open('template_921.html', 'r', encoding='utf-8') as f:
        t921 = f.read()
    with open('template_1010.html', 'r', encoding='utf-8') as f:
        t1010 = f.read()

    # Strip redundant stylesheet links from templates since all styles are now in css/bundle.min.css
    t921 = re.sub(r'<link[^>]*rel=[\"\']stylesheet[\"\'][^>]*>', '', t921)
    t1010 = re.sub(r'<link[^>]*rel=[\"\']stylesheet[\"\'][^>]*>', '', t1010)

    templates_and_modals = f'''
<!-- Template Layout 921 -->
<template id="template-layout-921">
{t921}
</template>

<!-- Template Layout 1010 -->
<template id="template-layout-1010">
{t1010}
</template>

<!-- WoodMart Quick View Popup Modal (Layout 921) -->
<div id="wd-quickview-backdrop" class="wd-modal-backdrop" onclick="window.DeshiMart.closeQuickView()"></div>
<div id="wd-quickview-modal" class="wd-quickview-popup" role="dialog" aria-modal="true">
  <div class="wd-popup-container">
    <button class="wd-popup-close-btn" onclick="window.DeshiMart.closeQuickView()" aria-label="Close">&times;</button>
    <div id="wd-quickview-content"></div>
  </div>
</div>

<!-- WoodMart Checkout Modal (Layout 1010) -->
<div id="wd-checkout-backdrop" class="wd-modal-backdrop" onclick="window.DeshiMart.closeCheckout()"></div>
<div id="wd-checkout-modal" class="wd-checkout-popup" role="dialog" aria-modal="true">
  <div class="wd-popup-container wd-checkout-container">
    <button class="wd-popup-close-btn" onclick="window.DeshiMart.closeCheckout()" aria-label="Close">&times;</button>
    <div id="wd-checkout-content"></div>
  </div>
</div>

<!-- Order Confirmation Success Modal -->
<div id="wd-order-success-modal" class="wd-modal-backdrop">
  <div class="wd-order-success-card">
    <div class="wd-success-icon-wrap">
      <svg class="wd-check-svg" viewBox="0 0 52 52">
        <circle class="wd-check-circle" cx="26" cy="26" r="25" fill="none"/>
        <path class="wd-check-path" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
      </svg>
    </div>
    <h3 class="wd-success-title">অর্ডার সফলভাবে গ্রহণ করা হয়েছে!</h3>
    <p class="wd-success-subtitle">ধন্যবাদ! আমাদের প্রতিনিধি খুব শীঘ্রই আপনার ঠিকানায় ডেলিভারির বিষয়ে যোগাযোগ করবেন।</p>
    <div id="wd-order-invoice-details" class="wd-invoice-box"></div>
    <button class="button" style="background:var(--wd-primary-color); color:#fff; border:none; padding:12px 24px; border-radius:4px; font-weight:700; cursor:pointer; margin-top:20px; width:100%;" onclick="window.DeshiMart.closeOrderSuccess()">নতুন অর্ডার করুন</button>
  </div>
</div>


<!-- Desktop Sticky Navbar with Logo -->
<div id="dm-sticky-navbar" class="dm-desktop-sticky">
  <div class="dm-sticky-inner">
    <div class="dm-sticky-logo">
      <a href="#" onclick="window.scrollTo({{top:0, behavior:'smooth'}}); return false;" aria-label="Deshi Mart Home">
        <img src="./wp-content/uploads/2026/09/logo-1.png" alt="Deshi Mart" width="138" height="40" />
      </a>
    </div>
    <nav class="dm-sticky-nav-links" aria-label="Sticky Category Navigation">
      <a href="javascript:void(0)" onclick="window.DeshiMart.scrollToCategory('ghee')">Ghee</a>
      <a href="javascript:void(0)" onclick="window.DeshiMart.scrollToCategory('oil')">Oil</a>
      <a href="javascript:void(0)" onclick="window.DeshiMart.scrollToCategory('honey')">Honey &amp; Dates</a>
      <a href="javascript:void(0)" onclick="window.DeshiMart.scrollToCategory('tea')">Tea</a>
      <a href="javascript:void(0)" onclick="window.DeshiMart.scrollToCategory('nuts')">Nuts</a>
      <a href="javascript:void(0)" onclick="window.DeshiMart.scrollToCategory('spices')">Spices</a>
      <a href="javascript:void(0)" onclick="window.DeshiMart.scrollToCategory('shutki')">Shutki</a>
      <a href="javascript:void(0)" onclick="window.DeshiMart.scrollToCategory('all')">All Products</a>
    </nav>
    <div class="dm-sticky-actions">
      <div class="dm-sticky-cart-btn" onclick="window.DeshiMart.openCheckout();" role="button" tabindex="0" aria-label="View Cart">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path><line x1="3" y1="6" x2="21" y2="6"></line><path d="M16 10a4 4 0 0 1-8 0"></path></svg>
        <span class="dm-sticky-cart-count wd-tools-count">0</span>
      </div>
      <button class="dm-sticky-order-cta" onclick="window.DeshiMart.openCheckout();" aria-label="Order Now">অর্ডার করুন</button>
    </div>
  </div>
</div>

<!-- Mobile Sticky Header with Logo -->
<div id="dm-mobile-sticky-header" class="dm-mobile-sticky">
  <button class="dm-mob-icon-btn" onclick="window.DeshiMart.scrollToCategory('all')" aria-label="Categories">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
  </button>
  <a href="#" onclick="window.scrollTo({{top:0, behavior:'smooth'}}); return false;" class="dm-mob-logo" aria-label="Deshi Mart Home">
    <img src="./wp-content/uploads/2026/09/logo-1.png" alt="Deshi Mart" width="120" height="32" />
  </a>
  <div class="dm-mob-icon-btn" onclick="window.DeshiMart.openCheckout();" role="button" tabindex="0" aria-label="View Cart">
    <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path><line x1="3" y1="6" x2="21" y2="6"></line><path d="M16 10a4 4 0 0 1-8 0"></path></svg>
    <span class="dm-mob-cart-badge wd-tools-count">0</span>
  </div>
</div>

<!-- Modern Mobile Bottom Navigation Bar -->
<nav id="dm-mobile-bottom-nav" class="dm-bottom-nav" aria-label="Mobile Navigation">
  <a href="javascript:void(0)" class="dm-bottom-nav-item active" onclick="window.scrollTo({{top:0, behavior:'smooth'}}); return false;">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
    <span>হোম</span>
  </a>
  <a href="javascript:void(0)" class="dm-bottom-nav-item" onclick="window.DeshiMart.openMobileMenu(); return false;">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
    <span>মেনু</span>
  </a>
  <a href="javascript:void(0)" class="dm-bottom-nav-item" onclick="window.DeshiMart.openSearch(); return false;">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
    <span>সার্চ</span>
  </a>
  <a href="javascript:void(0)" class="dm-bottom-nav-item dm-bottom-cart-item" onclick="window.DeshiMart.openCartDrawer(); return false;">
    <span class="dm-bottom-cart-badge wd-tools-count">0</span>
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path><line x1="3" y1="6" x2="21" y2="6"></line><path d="M16 10a4 4 0 0 1-8 0"></path></svg>
    <span>কার্ট</span>
  </a>
  <a href="javascript:void(0)" class="dm-bottom-nav-item" onclick="window.DeshiMart.openProfile(); return false;">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
    <span>প্রোফাইল</span>
  </a>
</nav>

<script src="js/products-data.js"></script>
<script src="js/app.js"></script>
'''

    html = html.replace('</body>', templates_and_modals + '\n</body>')

    # 11. Strict elimination of ALL emojis across html
    for em in ['\U0001F525', '\U0001F33F', '\U0001F512', '\u26A1', '\u2728', '\U0001F6D2', '\U0001F4E6', '\u2B50']:
        html = html.replace(em, '')

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print('Successfully generated final index.html! File size:', os.path.getsize('index.html'))

if __name__ == '__main__':
    main()
