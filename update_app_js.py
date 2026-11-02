# -*- coding: utf-8 -*-
with open('js/app.js', 'r', encoding='utf-8') as f:
    code = f.read()

pos_search = code.find('  // --- Instant Dropdown Search with Deep Keyword & Hashtag Support ---')
if pos_search == -1:
    pos_search = code.find('  // --- Instant Dropdown Search ---')
pos_checkout = code.find('  // --- WoodMart Checkout Modal (Layout 1010) ---')

new_middle = '''  // --- Instant Dropdown Search with Deep Keyword & Hashtag Support ---
  function initInstantSearch() {
    var searchForms = document.querySelectorAll('.searchform');
    searchForms.forEach(function (form) {
      var input = form.querySelector('input[type="text"], input[name="s"]');
      if (!input) return;

      var dropdown = form.querySelector('.wd-search-results-dropdown');
      if (!dropdown) {
        dropdown = document.createElement('div');
        dropdown.className = 'wd-search-results-dropdown';
        form.style.position = 'relative';
        form.appendChild(dropdown);
      }

      function performSearch(query) {
        query = query.trim().toLowerCase();
        if (query.length < 2) {
          dropdown.style.display = 'none';
          dropdown.innerHTML = '';
          return;
        }

        var products = window.DESHI_MART_PRODUCTS || [];
        var matches = [];

        products.forEach(function (p) {
          var score = 0;
          var matchedKeyword = '';

          // 1. Direct title match
          if (p.title && p.title.toLowerCase().indexOf(query) !== -1) {
            score += 100;
          }
          // 2. English title match
          if (p.englishTitle && p.englishTitle.toLowerCase().indexOf(query) !== -1) {
            score += 80;
          }
          // 3. Category match
          if ((p.category && p.category.toLowerCase().indexOf(query) !== -1) ||
              (p.categoryName && p.categoryName.toLowerCase().indexOf(query) !== -1)) {
            score += 60;
          }
          // 4. Hashtag match
          if (p.hashtags && p.hashtags.some(function (h) {
            var cleanH = h.toLowerCase().replace('#', '');
            var cleanQ = query.replace('#', '');
            if (cleanH.indexOf(cleanQ) !== -1 || cleanQ.indexOf(cleanH) !== -1) {
              matchedKeyword = h;
              return true;
            }
            return false;
          })) {
            score += 70;
          }
          // 5. Keywords array match
          if (p.keywords && p.keywords.some(function (k) {
            if (k.toLowerCase().indexOf(query) !== -1 || query.indexOf(k.toLowerCase()) !== -1) {
              if (!matchedKeyword) matchedKeyword = k;
              return true;
            }
            return false;
          })) {
            score += 50;
          }
          // 6. Brand match
          if (p.brand && p.brand.toLowerCase().indexOf(query) !== -1) {
            score += 40;
          }

          if (score > 0) {
            matches.push({ product: p, score: score, matchedKeyword: matchedKeyword });
          }
        });

        // Sort by relevance score
        matches.sort(function (a, b) { return b.score - a.score; });

        if (matches.length === 0) {
          dropdown.innerHTML = '<div class="wd-search-suggestions-box">' +
                               '  <div class="wd-search-suggestions-title">কোনো পণ্য খুঁজে পাওয়া যায়নি। জনপ্রিয় কিওয়ার্ড বা হ্যাশট্যাগ দিয়ে খুঁজুন:</div>' +
                               '  <div class="wd-search-suggestions-chips">' +
                               '    <span class="wd-search-sugg-chip" data-tag="ঘি" onclick="window.DeshiMart.searchByHashtag(this.getAttribute(\\'data-tag\\'))">#ঘি</span>' +
                               '    <span class="wd-search-sugg-chip" data-tag="মধু" onclick="window.DeshiMart.searchByHashtag(this.getAttribute(\\'data-tag\\'))">#মধু</span>' +
                               '    <span class="wd-search-sugg-chip" data-tag="কালমি" onclick="window.DeshiMart.searchByHashtag(this.getAttribute(\\'data-tag\\'))">#কালমি_খেজুর</span>' +
                               '    <span class="wd-search-sugg-chip" data-tag="তেল" onclick="window.DeshiMart.searchByHashtag(this.getAttribute(\\'data-tag\\'))">#তিলের_তেল</span>' +
                               '    <span class="wd-search-sugg-chip" data-tag="চা" onclick="window.DeshiMart.searchByHashtag(this.getAttribute(\\'data-tag\\'))">#মোরিঙ্গা_চা</span>' +
                               '  </div>' +
                               '</div>';
          dropdown.style.display = 'block';
          return;
        }

        var html = '<div class="wd-search-dropdown-header">' +
                   '  <span>পণ্য পাওয়া গেছে (' + matches.length + ' টি)</span>' +
                   '  <span>Enter চাপলে প্রথম পণ্যটি ওপেন হবে</span>' +
                   '</div>';

        matches.slice(0, 6).forEach(function (m) {
          var p = m.product;
          var curVar = p.variations[0];
          var titleDisplay = p.title;

          // Highlight matching text if in title
          var qRegex = new RegExp('(' + query.replace(/[-\\/\\\\^$*+?.()|[\\]{}]/g, '\\\\$&') + ')', 'gi');
          if (titleDisplay.match(qRegex)) {
            titleDisplay = titleDisplay.replace(qRegex, '<span class="wd-search-highlight">$1</span>');
          }

          var keywordBadge = m.matchedKeyword ? '<span class="wd-search-match-chip">' + m.matchedKeyword + '</span>' : '';

          html += '<div class="wd-search-result-item" data-product-id="' + p.id + '">' +
                  '  <img src="' + p.images[0] + '" alt="' + p.title + '" />' +
                  '  <div class="wd-search-result-info">' +
                  '    <div class="wd-search-result-title">' + titleDisplay + keywordBadge + '</div>' +
                  '    <div style="display:flex; align-items:center; gap:8px;">' +
                  '      <span class="wd-search-result-price">৳ ' + curVar.price.toLocaleString() + '</span>' +
                  (curVar.regularPrice ? '<span style="font-size:11px; color:#94a3b8; text-decoration:line-through;">৳ ' + curVar.regularPrice.toLocaleString() + '</span>' : '') +
                  '      <span style="font-size:11px; background:#f1f5f9; color:#64748b; padding:1px 6px; border-radius:4px;">' + (p.categoryName || p.category) + '</span>' +
                  '    </div>' +
                  '  </div>' +
                  '  <button type="button" class="button" style="background:var(--wd-primary-color); color:#fff; border:none; padding:4px 10px; font-size:12px; border-radius:4px; font-weight:600; cursor:pointer;">দেখুন</button>' +
                  '</div>';
        });

        dropdown.innerHTML = html;
        dropdown.style.display = 'block';

        dropdown.querySelectorAll('.wd-search-result-item').forEach(function (item) {
          item.addEventListener('click', function () {
            var pid = parseInt(item.getAttribute('data-product-id'), 10);
            dropdown.style.display = 'none';
            input.value = '';
            openQuickView(pid);
          });
        });
      }

      input.addEventListener('input', function () {
        performSearch(input.value);
      });

      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var query = input.value.trim().toLowerCase();
        if (query.length > 0) {
          var products = window.DESHI_MART_PRODUCTS || [];
          var match = products.find(function (p) {
            return (p.title && p.title.toLowerCase().indexOf(query) !== -1) ||
                   (p.englishTitle && p.englishTitle.toLowerCase().indexOf(query) !== -1) ||
                   (p.category && p.category.toLowerCase().indexOf(query) !== -1) ||
                   (p.keywords && p.keywords.some(function(k){ return k.toLowerCase().indexOf(query) !== -1; }));
          });
          if (match) {
            dropdown.style.display = 'none';
            input.value = '';
            openQuickView(match.id);
          }
        }
      });

      document.addEventListener('click', function (e) {
        if (!form.contains(e.target)) {
          dropdown.style.display = 'none';
        }
      });
    });
  }

  function searchByHashtag(tag) {
    var clean = tag.replace('#', '');
    var searchInputs = document.querySelectorAll('.searchform input[type="text"], .searchform input[name="s"]');
    if (searchInputs.length > 0) {
      searchInputs[0].value = clean;
      searchInputs[0].focus();
      searchInputs[0].dispatchEvent(new Event('input'));
      closeQuickView();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  // --- Premium Product Detail Modal (Above Fold View + Deep Scrollable Details) ---
  function openQuickView(productIdOrTitle) {
    var product = getProduct(productIdOrTitle);
    if (!product) return;

    currentQuickViewProduct = product;
    currentSelectedVarIndex = 0;

    var container = document.getElementById('wd-quickview-content');
    if (!container) return;

    var modal = document.getElementById('wd-quickview-modal');
    var popupContainer = modal ? modal.querySelector('.wd-popup-container') : null;
    if (popupContainer) {
      popupContainer.classList.add('wd-product-detail-container');
    }

    var curVar = product.variations[0];
    var discountPercent = curVar.regularPrice ? Math.round(((curVar.regularPrice - curVar.price) / curVar.regularPrice) * 100) : 0;

    // 1. Thumbnails HTML
    var thumbsHtml = '';
    product.images.forEach(function (imgSrc, idx) {
      var activeClass = (idx === 0) ? ' active' : '';
      thumbsHtml += '<img src="' + imgSrc + '" alt="' + product.title + '" class="wd-pd-thumb-btn' + activeClass + '" onclick="window.DeshiMart.setGalleryImage(this.src, this)" />';
    });

    // 2. Swatches (Variation / Weight)
    var swatchesHtml = '';
    product.variations.forEach(function (v, idx) {
      var activeClass = (idx === 0) ? ' active' : '';
      swatchesHtml += '<button type="button" class="wd-pd-swatch-btn' + activeClass + '" data-var-index="' + idx + '" onclick="window.DeshiMart.selectVariation(' + idx + ', this)">' + v.name + '</button>';
    });

    // 3. Nutrition Facts Table
    var nutritionHtml = '';
    if (product.nutrition) {
      nutritionHtml = '<table class="wd-pd-table"><tbody>';
      for (var key in product.nutrition) {
        nutritionHtml += '<tr><td class="label-col">' + key + '</td><td class="val-col">' + product.nutrition[key] + '</td></tr>';
      }
      nutritionHtml += '</tbody></table>';
    } else {
      nutritionHtml = '<p style="color:#64748b; font-size:14px;">পুষ্টিগুণ তথ্য শীঘ্রই যুক্ত করা হবে।</p>';
    }

    // 4. Specifications Table
    var specsHtml = '';
    if (product.specifications) {
      specsHtml = '<table class="wd-pd-table"><tbody>';
      for (var sKey in product.specifications) {
        specsHtml += '<tr><td class="label-col">' + sKey + '</td><td class="val-col">' + product.specifications[sKey] + '</td></tr>';
      }
      specsHtml += '</tbody></table>';
    } else {
      specsHtml = '<p style="color:#64748b; font-size:14px;">স্পেসিফিকেশন তথ্য শীঘ্রই যুক্ত করা হবে।</p>';
    }

    // 5. Hashtags & Keywords Pills
    var hashtagsHtml = '';
    if (product.hashtags && product.hashtags.length > 0) {
      hashtagsHtml = '<div class="wd-pd-hashtags-wrap">' +
                     '  <div class="wd-pd-hashtags-instruction">যেকোনো হ্যাশট্যাগে ক্লিক করে সম্পর্কিত পণ্য সহজে খুঁজুন:</div>' +
                     '  <div class="wd-pd-hashtags-list">';
      product.hashtags.forEach(function (h) {
        hashtagsHtml += '<span class="wd-pd-hashtag-pill" data-tag="' + h + '" onclick="window.DeshiMart.searchByHashtag(this.getAttribute(\\'data-tag\\'))">' + h + '</span>';
      });
      hashtagsHtml += '  </div>' +
                      '</div>';
    }

    // 6. Customer Reviews List
    var reviewsHtml = '';
    if (product.reviews && product.reviews.length > 0) {
      reviewsHtml = '<div class="wd-pd-reviews-list">';
      product.reviews.forEach(function (rev) {
        reviewsHtml += '<div class="wd-pd-review-card">' +
                       '  <div class="wd-pd-review-top">' +
                       '    <div>' +
                       '      <span class="wd-pd-reviewer-name">' + rev.name + '</span>' +
                       '      <span style="display:inline-block; margin-left:8px; color:#16a34a; font-size:12px; font-weight:600;">ভেরিফাইড ক্রেতা ✓</span>' +
                       '    </div>' +
                       '    <span class="wd-pd-review-date">' + rev.date + '</span>' +
                       '  </div>' +
                       '  <div style="color:#f59e0b; font-size:13px; margin-bottom:6px;">★★★★★</div>' +
                       '  <p class="wd-pd-review-text">' + rev.comment + '</p>' +
                       '</div>';
      });
      reviewsHtml += '</div>';
    } else {
      reviewsHtml = '<p style="color:#64748b; font-size:14px;">এই পণ্যে এখনো কোনো রিভিউ নেই। প্রথম রিভিউ দিন!</p>';
    }

    // 7. Related Products
    var allProducts = window.DESHI_MART_PRODUCTS || [];
    var related = allProducts.filter(function (p) {
      return p.id !== product.id && (p.category === product.category);
    }).slice(0, 4);

    var relatedHtml = '';
    if (related.length > 0) {
      relatedHtml = '<div class="wd-pd-related-section">' +
                    '  <div class="wd-pd-related-title">একই ক্যাটাগরির সম্পর্কিত অন্যান্য পণ্য</div>' +
                    '  <div class="wd-pd-related-grid">';
      related.forEach(function (rp) {
        var rVar = rp.variations[0];
        relatedHtml += '<div class="wd-pd-related-card" onclick="window.DeshiMart.openQuickView(' + rp.id + ')">' +
                       '  <img src="' + rp.images[0] + '" alt="' + rp.title + '" />' +
                       '  <div class="wd-pd-related-card-title">' + rp.title + '</div>' +
                       '  <div class="wd-pd-related-card-price">৳ ' + rVar.price.toLocaleString() + '</div>' +
                       '</div>';
      });
      relatedHtml += '  </div>' +
                     '</div>';
    }

    // Full Modal HTML Template
    var fullHtml = '' +
      '<div class="wd-pd-topbar">' +
      '  <div class="wd-pd-breadcrumb">' +
      '    <a href="#" onclick="window.DeshiMart.closeQuickView(); return false;">হোম</a> / ' +
      '    <a href="javascript:void(0)" onclick="window.DeshiMart.scrollToCategory(\\' + product.category + '\\'); return false;">' + (product.categoryName || product.category) + '</a> / ' +
      '    <span style="color:#0f172a; font-weight:600;">' + product.title + '</span>' +
      '  </div>' +
      '  <div class="wd-pd-stock-badge">' +
      '    <span class="wd-pd-stock-dot"></span>' +
      '    <span>স্টকে আছে (ইন স্টক)</span>' +
      '  </div>' +
      '</div>' +

      '<div class="wd-pd-main-grid">' +
      '  <!-- Left Column: Gallery -->' +
      '  <div class="wd-pd-gallery">' +
      '    <div class="wd-pd-main-image-wrap">' +
      (discountPercent > 0 ? '      <span class="wd-pd-discount-badge">-' + discountPercent + '% ছাড়</span>' : '') +
      '      <img id="wd-pd-active-img" src="' + product.images[0] + '" alt="' + product.title + '" class="wd-pd-main-image" />' +
      '    </div>' +
      '    <div class="wd-pd-thumbnails">' + thumbsHtml + '</div>' +
      '  </div>' +

      '  <!-- Right Column: Purchase Info -->' +
      '  <div class="wd-pd-info">' +
      '    <div class="wd-pd-category-tag">' + (product.categoryName || product.category) + '</div>' +
      '    <h1 class="wd-pd-title">' + product.title + '</h1>' +

      '    <div class="wd-pd-rating-row">' +
      '      <span class="wd-pd-stars">★★★★★</span>' +
      '      <span class="wd-pd-reviews-count">(৫.০ রেটিং | ' + (product.reviewsCount || 3) + ' টি ভেরিফাইড রিভিউ)</span>' +
      '    </div>' +

      '    <div class="wd-pd-price-box" id="wd-pd-price-container">' +
      '      <span class="wd-pd-current-price">৳ ' + curVar.price.toLocaleString() + '</span>' +
      (curVar.regularPrice ? '      <span class="wd-pd-regular-price">৳ ' + curVar.regularPrice.toLocaleString() + '</span>' : '') +
      (discountPercent > 0 ? '      <span class="wd-pd-savings-pill">' + discountPercent + '% সাশ্রয়</span>' : '') +
      '    </div>' +

      '    <label class="wd-pd-section-label">পরিমাণ / সাইজ নির্বাচন করুন:</label>' +
      '    <div class="wd-pd-swatches-row">' + swatchesHtml + '</div>' +

      '    <div class="wd-pd-action-row">' +
      '      <div class="wd-pd-stepper">' +
      '        <button type="button" class="wd-pd-stepper-btn" onclick="window.DeshiMart.changeQuickViewQty(-1)">-</button>' +
      '        <input type="number" id="wd-pd-qty-input" class="wd-pd-stepper-input" value="1" min="1" readonly />' +
      '        <button type="button" class="wd-pd-stepper-btn" onclick="window.DeshiMart.changeQuickViewQty(1)">+</button>' +
      '      </div>' +
      '      <button type="button" class="wd-pd-btn-atc" id="wd-pd-atc-btn" onclick="window.DeshiMart.addToCartFromQuickView(this)">' +
      '        কার্টে যোগ করুন' +
      '      </button>' +
      '    </div>' +

      '    <button type="button" class="wd-pd-btn-buy-now" onclick="window.DeshiMart.buyNowFromQuickView()">' +
      '      এখনই অর্ডার করুন (ক্যাশ অন ডেলিভারি)' +
      '    </button>' +

      '    <div class="wd-pd-fast-order-row">' +
      '      <a href="https://wa.me/8801738734000?text=' + encodeURIComponent('হ্যালো, আমি ' + product.title + ' অর্ডার করতে চাই।') + '" target="_blank" class="wd-pd-contact-btn whatsapp">' +
      '        হোয়াটসঅ্যাপে অর্ডার' +
      '      </a>' +
      '      <a href="tel:+8801738734000" class="wd-pd-contact-btn call">' +
      '        সরাসরি কল করুন' +
      '      </a>' +
      '    </div>' +

      '    <div class="wd-pd-guarantees">' +
      '      <div class="wd-pd-guarantee-item">' +
      '        <svg class="wd-pd-guarantee-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>' +
      '        <span>১০০% খাঁটি ও নির্ভেজাল পণ্য</span>' +
      '      </div>' +
      '      <div class="wd-pd-guarantee-item">' +
      '        <svg class="wd-pd-guarantee-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>' +
      '        <span>ক্যাশ অন ডেলিভারি সুবিধা</span>' +
      '      </div>' +
      '      <div class="wd-pd-guarantee-item">' +
      '        <svg class="wd-pd-guarantee-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0"></path></svg>' +
      '        <span>সারা দেশে দ্রুত হোম ডেলিভারি</span>' +
      '      </div>' +
      '      <div class="wd-pd-guarantee-item">' +
      '        <svg class="wd-pd-guarantee-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>' +
      '        <span>সহজ রিটার্ন ও রিফান্ড পলিসি</span>' +
      '      </div>' +
      '    </div>' +
      '  </div>' +
      '</div>' +

      '<!-- Scroll Down: Full Product Details -->' +
      '<div class="wd-pd-details-section">' +
      '  <div class="wd-pd-section-header">পণ্যের বিস্তারিত বিবরণ ও স্পেসিফিকেশন</div>' +

      '  <div class="wd-pd-tab-nav">' +
      '    <button type="button" class="wd-pd-tab-btn active" data-tab="desc" onclick="window.DeshiMart.switchProductTab(this.getAttribute(\\'data-tab\\'), this)">বিস্তারিত বিবরণ</button>' +
      '    <button type="button" class="wd-pd-tab-btn" data-tab="nutrition" onclick="window.DeshiMart.switchProductTab(this.getAttribute(\\'data-tab\\'), this)">পুষ্টিগুণ ও উপাদান</button>' +
      '    <button type="button" class="wd-pd-tab-btn" data-tab="specs" onclick="window.DeshiMart.switchProductTab(this.getAttribute(\\'data-tab\\'), this)">স্পেসিফিকেশন</button>' +
      '    <button type="button" class="wd-pd-tab-btn" data-tab="hashtags" onclick="window.DeshiMart.switchProductTab(this.getAttribute(\\'data-tab\\'), this)">হ্যাশট্যাগ ও কিওয়ার্ডস</button>' +
      '    <button type="button" class="wd-pd-tab-btn" data-tab="reviews" onclick="window.DeshiMart.switchProductTab(this.getAttribute(\\'data-tab\\'), this)">কাস্টমার রিভিউ (' + (product.reviews ? product.reviews.length : 0) + ')</button>' +
      '  </div>' +

      '  <div id="wd-pd-tab-desc" class="wd-pd-tab-panel active">' +
      '    <div class="wd-pd-desc-content">' + product.description + '</div>' +
      (product.features && product.features.length > 0 ?
      '    <h4 style="font-size:16px; font-weight:700; color:#0f172a; margin:16px 0 10px 0;">পণ্যের প্রধান বৈশিষ্ট্যসমূহ:</h4>' +
      '    <ul class="wd-pd-features-list">' + product.features.map(function(f){ return '<li>' + f + '</li>'; }).join('') + '</ul>' : '') +
      '  </div>' +

      '  <div id="wd-pd-tab-nutrition" class="wd-pd-tab-panel">' +
      nutritionHtml +
      '  </div>' +

      '  <div id="wd-pd-tab-specs" class="wd-pd-tab-panel">' +
      specsHtml +
      '  </div>' +

      '  <div id="wd-pd-tab-hashtags" class="wd-pd-tab-panel">' +
      hashtagsHtml +
      '  </div>' +

      '  <div id="wd-pd-tab-reviews" class="wd-pd-tab-panel">' +
      reviewsHtml +
      '  </div>' +

      relatedHtml +
      '</div>';

    container.innerHTML = fullHtml;

    // Show modal
    var backdrop = document.getElementById('wd-quickview-backdrop');
    if (backdrop) backdrop.classList.add('is-open');
    if (modal) {
      modal.classList.add('is-open');
      if (popupContainer) popupContainer.scrollTop = 0;
    }
  }

  function switchProductTab(tabName, btn) {
    var modal = document.getElementById('wd-quickview-modal');
    if (!modal) return;

    modal.querySelectorAll('.wd-pd-tab-btn').forEach(function (b) { b.classList.remove('active'); });
    if (btn) btn.classList.add('active');

    modal.querySelectorAll('.wd-pd-tab-panel').forEach(function (panel) {
      panel.classList.remove('active');
    });

    var targetPanel = modal.querySelector('#wd-pd-tab-' + tabName);
    if (targetPanel) {
      targetPanel.classList.add('active');
    }
  }

  function selectVariation(idx, btn) {
    if (!currentQuickViewProduct) return;
    currentSelectedVarIndex = idx;
    var curVar = currentQuickViewProduct.variations[idx];

    var modal = document.getElementById('wd-quickview-modal');
    if (modal) {
      modal.querySelectorAll('.wd-pd-swatch-btn').forEach(function (b) { b.classList.remove('active'); });
      if (btn) btn.classList.add('active');

      var priceBox = modal.querySelector('#wd-pd-price-container');
      if (priceBox) {
        var discountPercent = curVar.regularPrice ? Math.round(((curVar.regularPrice - curVar.price) / curVar.regularPrice) * 100) : 0;
        var pboxHtml = '<span class="wd-pd-current-price">৳ ' + curVar.price.toLocaleString() + '</span>' +
                       (curVar.regularPrice ? '<span class="wd-pd-regular-price">৳ ' + curVar.regularPrice.toLocaleString() + '</span>' : '') +
                       (discountPercent > 0 ? '<span class="wd-pd-savings-pill">' + discountPercent + '% সাশ্রয়</span>' : '');
        priceBox.innerHTML = pboxHtml;
      }
    }
  }

  function setGalleryImage(src, thumbItem) {
    var modal = document.getElementById('wd-quickview-modal');
    if (!modal) return;

    var activeImg = modal.querySelector('#wd-pd-active-img');
    if (activeImg) {
      activeImg.style.opacity = '0.4';
      setTimeout(function () {
        activeImg.src = src;
        activeImg.style.opacity = '1';
      }, 150);
    }

    modal.querySelectorAll('.wd-pd-thumb-btn').forEach(function (t) { t.classList.remove('active'); });
    if (thumbItem) thumbItem.classList.add('active');
  }

  function changeQuickViewQty(delta) {
    var qtyInput = document.getElementById('wd-pd-qty-input');
    if (!qtyInput) return;
    var val = parseInt(qtyInput.value, 10) || 1;
    val = Math.max(1, val + delta);
    qtyInput.value = val;
  }

  function closeQuickView() {
    var backdrop = document.getElementById('wd-quickview-backdrop');
    var modal = document.getElementById('wd-quickview-modal');
    if (backdrop) backdrop.classList.remove('is-open');
    if (modal) modal.classList.remove('is-open');
  }

  // --- Add to Cart Unified Engine with Visual Feedback ---
  function addToCartFromQuickView(btn) {
    if (!currentQuickViewProduct) return;
    var curVar = currentQuickViewProduct.variations[currentSelectedVarIndex];
    var qtyInput = document.getElementById('wd-pd-qty-input');
    var qty = qtyInput ? (parseInt(qtyInput.value, 10) || 1) : 1;

    // Visual button feedback
    if (btn) {
      var origText = btn.innerHTML;
      btn.innerHTML = 'যোগ হচ্ছে...';
      btn.disabled = true;

      setTimeout(function () {
        btn.classList.add('btn-added-success');
        btn.innerHTML = 'কার্টে যুক্ত হয়েছে ✓';

        setTimeout(function () {
          btn.classList.remove('btn-added-success');
          btn.innerHTML = origText;
          btn.disabled = false;
        }, 1200);
      }, 200);
    }

    var existing = cart.find(function (item) {
      return item.productId === currentQuickViewProduct.id && item.variationName === curVar.name;
    });

    if (existing) {
      existing.quantity += qty;
    } else {
      cart.push({
        productId: currentQuickViewProduct.id,
        title: currentQuickViewProduct.title,
        variationName: curVar.name,
        price: curVar.price,
        image: currentQuickViewProduct.images[0],
        quantity: qty
      });
    }

    saveCart();
    triggerCartBadgeBounce();

    // Slide out side cart drawer
    setTimeout(function () {
      openCartDrawer();
    }, 400);
  }

  function buyNowFromQuickView() {
    if (!currentQuickViewProduct) return;
    var curVar = currentQuickViewProduct.variations[currentSelectedVarIndex];
    var qtyInput = document.getElementById('wd-pd-qty-input');
    var qty = qtyInput ? (parseInt(qtyInput.value, 10) || 1) : 1;

    cart = [{
      productId: currentQuickViewProduct.id,
      title: currentQuickViewProduct.title,
      variationName: curVar.name,
      price: curVar.price,
      image: currentQuickViewProduct.images[0],
      quantity: qty
    }];

    saveCart();
    closeQuickView();
    openCheckout();
  }

  function quickBuyNow(productId) {
    var product = getProduct(productId);
    if (!product) return;

    var firstVar = product.variations[0];
    cart = [{
      productId: product.id,
      title: product.title,
      variationName: firstVar.name,
      price: firstVar.price,
      image: product.images[0],
      quantity: 1
    }];

    saveCart();
    openCheckout();
  }

  function triggerCartBadgeBounce() {
    var headerCounts = document.querySelectorAll('.wd-header-cart .wd-tools-count, .whb-col-right .wd-cart-number, .wd-toolbar-cart .wd-tools-count');
    headerCounts.forEach(function (el) {
      el.classList.remove('wd-cart-badge-bounce');
      void el.offsetWidth; // trigger reflow
      el.classList.add('wd-cart-badge-bounce');
    });
  }

  // --- Side Cart Drawer (Authentic WoodMart Experience) ---
  function openCartDrawer() {
    renderSideCart();
    var drawer = document.querySelector('.cart-widget-side');
    if (drawer) drawer.classList.add('wd-opened');
    document.body.classList.add('wd-close-side-opened');
  }

  function closeCartDrawer() {
    var drawer = document.querySelector('.cart-widget-side');
    if (drawer) drawer.classList.remove('wd-opened');
    document.body.classList.remove('wd-close-side-opened');
  }

  function renderSideCart() {
    var container = document.querySelector('.widget_shopping_cart_content');
    if (!container) return;

    if (cart.length === 0) {
      container.innerHTML = '<div style="padding:60px 25px; text-align:center; color:#64748b;">' +
                            '  <div style="font-size:42px; margin-bottom:12px; opacity:0.4;">🛒</div>' +
                            '  <h3 style="font-size:17px; font-weight:700; color:#1e293b; margin-bottom:8px;">আপনার শপিং ব্যাগ খালি রয়েছে</h3>' +
                            '  <p style="font-size:13px; color:#64748b; margin-bottom:20px;">আমাদের ফ্রেশ দেশি খাঁটি পণ্য দেখতে কেনাকাটা শুরু করুন।</p>' +
                            '  <button class="wd-cart-btn-checkout" style="max-width:200px; margin:0 auto;" onclick="window.DeshiMart.closeCartDrawer()">কেনাকাটা করুন</button>' +
                            '</div>';
      return;
    }

    var subtotal = getCartSubtotal();
    var freeShippingGoal = 1500;
    var remaining = Math.max(0, freeShippingGoal - subtotal);
    var progressPercent = Math.min(100, Math.round((subtotal / freeShippingGoal) * 100));

    // Free shipping bar HTML
    var shippingBarHtml = '<div class="wd-free-shipping-bar">' +
                          '  <div class="wd-free-shipping-text">' +
                          (remaining > 0 ?
                          '    <span>আর মাত্র <strong>৳ ' + remaining.toLocaleString() + '</strong> যোগ করলেই ফ্রি ডেলিভারি!</span>' :
                          '    <span style="color:#16a34a; font-weight:700;">অভিনন্দন! আপনি ফ্রি ডেলিভারি পেয়েছেন!</span>') +
                          '    <span style="font-size:11px; font-weight:700;">' + progressPercent + '%</span>' +
                          '  </div>' +
                          '  <div class="wd-free-shipping-progress">' +
                          '    <div class="wd-free-shipping-progress-fill" style="width:' + progressPercent + '%;"></div>' +
                          '  </div>' +
                          '</div>';

    // Items list
    var itemsHtml = '';
    cart.forEach(function (item, index) {
      itemsHtml += '<div class="wd-cart-item-row">' +
                   '  <img src="' + item.image + '" alt="' + item.title + '" class="wd-cart-item-thumb" />' +
                   '  <div class="wd-cart-item-info">' +
                   '    <div class="wd-cart-item-title" title="' + item.title + '">' + item.title + '</div>' +
                   '    <span class="wd-cart-item-variant">' + item.variationName + '</span>' +
                   '    <div class="wd-cart-item-actions">' +
                   '      <div class="wd-cart-qty-stepper">' +
                   '        <button type="button" class="wd-cart-qty-btn" onclick="window.DeshiMart.updateCartQty(' + index + ', -1)">-</button>' +
                   '        <input type="text" class="wd-cart-qty-input" value="' + item.quantity + '" readonly />' +
                   '        <button type="button" class="wd-cart-qty-btn" onclick="window.DeshiMart.updateCartQty(' + index + ', 1)">+</button>' +
                   '      </div>' +
                   '      <span class="wd-cart-item-subtotal">৳ ' + (item.price * item.quantity).toLocaleString() + '</span>' +
                   '    </div>' +
                   '  </div>' +
                   '  <button type="button" class="wd-cart-item-remove" onclick="window.DeshiMart.removeCartItem(' + index + ')" aria-label="Remove">✕</button>' +
                   '</div>';
    });

    var footerHtml = '<div class="wd-cart-drawer-footer">' +
                     '  <div class="wd-cart-subtotal-row">' +
                     '    <span>সর্বমোট:</span>' +
                     '    <span class="wd-cart-subtotal-val">৳ ' + subtotal.toLocaleString() + '</span>' +
                     '  </div>' +
                     '  <div class="wd-cart-shipping-note">ডেলিভারি চার্জ চেকআউটে যোগ হবে (ঢাকা ৳ ৬০ / ঢাকার বাইরে ৳ ১২০)</div>' +
                     '  <button type="button" class="wd-cart-btn-checkout" onclick="window.DeshiMart.openCheckout()">' +
                     '    অর্ডার সম্পন্ন করুন (চেকআউট)' +
                     '  </button>' +
                     '  <button type="button" class="wd-cart-btn-continue" onclick="window.DeshiMart.closeCartDrawer()">' +
                     '    আরও কেনাকাটা করুন' +
                     '  </button>' +
                     '</div>';

    container.innerHTML = shippingBarHtml +
                          '<div style="max-height:calc(100vh - 290px); overflow-y:auto;">' +
                          itemsHtml +
                          '</div>' +
                          footerHtml;
  }

  function updateCartQty(index, delta) {
    if (!cart[index]) return;
    cart[index].quantity += delta;
    if (cart[index].quantity <= 0) {
      cart.splice(index, 1);
    }
    saveCart();
    renderSideCart();
    triggerCartBadgeBounce();
  }

  function removeCartItem(index) {
    cart.splice(index, 1);
    saveCart();
    renderSideCart();
    triggerCartBadgeBounce();
  }
\n'''

new_code = code[:pos_search] + new_middle + code[pos_checkout:]

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(new_code)

print("Updated app.js successfully! Length:", len(new_code))
