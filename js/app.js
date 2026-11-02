/**
 * Deshi Mart - Authentic WoodMart Interactive Engine
 * Pixel-perfect 1:1 replica of https://demo7.itservicelab.com/
 * ZERO EMOJIS, High Performance, Authentic Layout 921 & Layout 1010
 */

(function () {
  'use strict';

  var cart = JSON.parse(localStorage.getItem('deshi_mart_cart') || '[]');
  var currentQuickViewProduct = null;
  var currentSelectedVarIndex = 0;
  var selectedDeliveryZone = 'dhaka'; // 'dhaka' (60) or 'outside' (120)
  var selectedPaymentMethod = 'cod';

  // --- Fast Product Lookup ---
  function getProduct(productIdOrTitle) {
    var products = window.DESHI_MART_PRODUCTS || [];
    if (!products || products.length === 0) return null;

    if (typeof productIdOrTitle === 'number') {
      var found = products.find(function (p) { return p.id === productIdOrTitle; });
      if (found) return found;
    }

    var query = String(productIdOrTitle).trim().toLowerCase();
    
    // Match by ID string
    var byId = products.find(function (p) { return String(p.id) === query; });
    if (byId) return byId;

    // Match by slug
    var bySlug = products.find(function (p) { return p.slug === query; });
    if (bySlug) return bySlug;

    // Match by title
    var byTitle = products.find(function (p) {
      return p.title.toLowerCase().indexOf(query) !== -1 || query.indexOf(p.title.toLowerCase()) !== -1;
    });
    if (byTitle) return byTitle;

    return products[0];
  }

  function saveCart() {
    localStorage.setItem('deshi_mart_cart', JSON.stringify(cart));
    updateCartBadges();
  }

  function getCartSubtotal() {
    return cart.reduce(function (sum, item) {
      return sum + (item.price * item.quantity);
    }, 0);
  }

  function updateCartBadges() {
    var count = cart.reduce(function (c, item) { return c + item.quantity; }, 0);
    var subtotal = getCartSubtotal();

    // Header count badges
    var headerCounts = document.querySelectorAll('.wd-header-cart .wd-tools-count, .whb-col-right .wd-cart-number, .wd-toolbar-cart .wd-tools-count');
    headerCounts.forEach(function (el) {
      el.textContent = count;
    });

    // Subtotal in header
    var subtotalEls = document.querySelectorAll('.wd-header-cart .subtotal-divider ~ .amount, .wd-header-cart .wd-cart-subtotal');
    subtotalEls.forEach(function (el) {
      el.innerHTML = '<bdi><span class="woocommerce-Price-currencySymbol">৳ </span>' + subtotal.toLocaleString() + '</bdi>';
    });
  }

  // --- Multi-Slider Engine (Authentic WoodMart Parallax & Style-3 Dots) ---
  function initHeroSliders() {
    var sliders = document.querySelectorAll('.wd-slider');
    sliders.forEach(function (sliderEl) {
      var wrap = sliderEl.querySelector('.wd-carousel-wrap');
      if (!wrap) return;

      var slides = wrap.querySelectorAll('.wd-slide');
      if (!slides || slides.length === 0) return;

      // Single slide: static banner (e.g. slider-32)
      if (slides.length <= 1) {
        slides.forEach(function (s) {
          s.classList.add('woodmart-loaded');
          var bg = s.querySelector('.wd-slide-bg');
          if (bg) bg.style.transform = 'none';
        });
        return;
      }

      var currentIdx = 0;
      var timer = null;
      var speed = parseInt(wrap.getAttribute('data-speed') || '3900', 10);
      var slidingSpeed = parseInt(wrap.getAttribute('data-sliding_speed') || '700', 10);

      // Find or build Style-3 pagination dots
      var paginUl = sliderEl.querySelector('.wd-nav-pagin');
      var dots = [];
      if (paginUl) {
        paginUl.innerHTML = '';
        for (var i = 0; i < slides.length; i++) {
          var li = document.createElement('li');
          li.setAttribute('data-index', i);
          li.innerHTML = '<span></span>';
          if (i === 0) {
            li.classList.add('wd-active');
            li.classList.add('active');
          }
          (function (index) {
            li.addEventListener('click', function (e) {
              e.preventDefault();
              e.stopPropagation();
              goTo(index);
              startAutoplay();
            });
          })(i);
          paginUl.appendChild(li);
        }
        dots = paginUl.querySelectorAll('li');
      }

      wrap.style.display = 'flex';
      wrap.style.transition = 'transform ' + (slidingSpeed / 1000) + 's cubic-bezier(0.22, 0.61, 0.36, 1)';
      wrap.style.width = (slides.length * 100) + '%';
      wrap.style.willChange = 'transform';

      slides.forEach(function (s, idx) {
        s.style.width = (100 / slides.length) + '%';
        s.style.flexShrink = '0';
        s.style.position = 'relative';
        s.classList.add('woodmart-loaded');
        var bg = s.querySelector('.wd-slide-bg');
        if (bg) {
          bg.style.transition = 'transform ' + (slidingSpeed / 1000) + 's cubic-bezier(0.22, 0.61, 0.36, 1)';
          bg.style.willChange = 'transform';
        }
      });

      function goTo(index) {
        currentIdx = index;
        var offset = -(currentIdx * (100 / slides.length));
        wrap.style.transform = 'translate3d(' + offset + '%, 0px, 0px)';

        // Parallax effect on slide background images
        slides.forEach(function (s, i) {
          var bg = s.querySelector('.wd-slide-bg');
          if (bg) {
            if (i === currentIdx) {
              bg.style.transform = 'translate3d(0%, 0px, 0px) scale(1)';
            } else if (i < currentIdx) {
              bg.style.transform = 'translate3d(-15%, 0px, 0px) scale(1.05)';
            } else {
              bg.style.transform = 'translate3d(15%, 0px, 0px) scale(1.05)';
            }
          }
        });

        // Update dots with authentic classes
        dots.forEach(function (d, i) {
          if (i === currentIdx) {
            d.classList.add('wd-active');
            d.classList.add('active');
          } else {
            d.classList.remove('wd-active');
            d.classList.remove('active');
          }
        });
      }

      function startAutoplay() {
        clearInterval(timer);
        timer = setInterval(function () {
          var next = (currentIdx + 1) % slides.length;
          goTo(next);
        }, speed);
      }

      // Initial state
      goTo(0);
      startAutoplay();

      sliderEl.addEventListener('mouseenter', function () { clearInterval(timer); });
      sliderEl.addEventListener('mouseleave', function () { startAutoplay(); });

      // Mobile Touch Swipe
      var startX = 0;
      var distThreshold = 40;
      sliderEl.addEventListener('touchstart', function (e) {
        startX = e.touches[0].clientX;
      }, { passive: true });

      sliderEl.addEventListener('touchend', function (e) {
        var diffX = e.changedTouches[0].clientX - startX;
        if (diffX > distThreshold) {
          goTo((currentIdx - 1 + slides.length) % slides.length);
          startAutoplay();
        } else if (diffX < -distThreshold) {
          goTo((currentIdx + 1) % slides.length);
          startAutoplay();
        }
      }, { passive: true });
    });
  }

  // --- Brand Logos Infinite Swiper Carousel ---
  function initBrandCarousel() {
    var carouselWidget = document.querySelector('.elementor-widget-image-carousel');
    if (!carouselWidget) return;

    var wrapper = carouselWidget.querySelector('.elementor-image-carousel.swiper-wrapper');
    if (!wrapper) return;

    var slides = wrapper.querySelectorAll('.swiper-slide');
    if (!slides || slides.length === 0) return;

    var currentOffset = 0;
    var timer = null;

    function getVisibleCount() {
      var w = window.innerWidth;
      if (w > 1024) return 5;
      if (w > 768) return 4;
      return 3;
    }

    function applyLayout() {
      var count = getVisibleCount();
      var itemWidthPercent = 100 / count;
      slides.forEach(function (slide) {
        slide.style.width = itemWidthPercent + '%';
        slide.style.flexShrink = '0';
      });
    }

    applyLayout();
    window.addEventListener('resize', function () {
      applyLayout();
      updatePosition();
    });

    var maxIndex = Math.max(0, slides.length - getVisibleCount());

    function updatePosition() {
      var count = getVisibleCount();
      maxIndex = Math.max(0, slides.length - count);
      var itemWidthPercent = 100 / count;
      wrapper.style.transform = 'translate3d(-' + (currentOffset * itemWidthPercent) + '%, 0px, 0px)';
    }

    function slideNext() {
      var count = getVisibleCount();
      maxIndex = Math.max(0, slides.length - count);
      if (currentOffset >= maxIndex) {
        currentOffset = 0;
      } else {
        currentOffset++;
      }
      updatePosition();
    }

    function slidePrev() {
      var count = getVisibleCount();
      maxIndex = Math.max(0, slides.length - count);
      if (currentOffset <= 0) {
        currentOffset = maxIndex;
      } else {
        currentOffset--;
      }
      updatePosition();
    }

    function startBrandAutoplay() {
      clearInterval(timer);
      timer = setInterval(slideNext, 3500);
    }

    startBrandAutoplay();

    carouselWidget.addEventListener('mouseenter', function () { clearInterval(timer); });
    carouselWidget.addEventListener('mouseleave', function () { startBrandAutoplay(); });

    var nextBtn = carouselWidget.querySelector('.elementor-swiper-button-next');
    var prevBtn = carouselWidget.querySelector('.elementor-swiper-button-prev');

    if (nextBtn) {
      nextBtn.addEventListener('click', function (e) {
        e.preventDefault();
        slideNext();
        startBrandAutoplay();
      });
    }

    if (prevBtn) {
      prevBtn.addEventListener('click', function (e) {
        e.preventDefault();
        slidePrev();
        startBrandAutoplay();
      });
    }
  }

  // --- Scroll & Viewport Animations ---
  function initScrollAnimations() {
    var animatedElements = document.querySelectorAll('.wd-animation-zoom-in, .wd-animation, .wd-product');
    if (!animatedElements || animatedElements.length === 0) return;

    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('wd-animated');
            entry.target.classList.add('wd-in');
            observer.unobserve(entry.target);
          }
        });
      }, { rootMargin: '0px 0px -50px 0px', threshold: 0.05 });

      animatedElements.forEach(function (el) {
        observer.observe(el);
      });
    } else {
      animatedElements.forEach(function (el) {
        el.classList.add('wd-animated');
        el.classList.add('wd-in');
      });
    }
  }

  // --- Sticky Header ---
  function initStickyHeader() {
    var header = document.querySelector('header.whb-header');
    if (!header) return;

    window.addEventListener('scroll', function () {
      if (window.scrollY > 120) {
        header.classList.add('whb-sticked');
      } else {
        header.classList.remove('whb-sticked');
      }
    }, { passive: true });
  }

  // --- Instant Dropdown Search with Deep Keyword & Hashtag Support ---
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
                               '    <span class="wd-search-sugg-chip" data-tag="ঘি" onclick="window.DeshiMart.searchByHashtag(this.getAttribute(\'data-tag\'))">#ঘি</span>' +
                               '    <span class="wd-search-sugg-chip" data-tag="মধু" onclick="window.DeshiMart.searchByHashtag(this.getAttribute(\'data-tag\'))">#মধু</span>' +
                               '    <span class="wd-search-sugg-chip" data-tag="কালমি" onclick="window.DeshiMart.searchByHashtag(this.getAttribute(\'data-tag\'))">#কালমি_খেজুর</span>' +
                               '    <span class="wd-search-sugg-chip" data-tag="তেল" onclick="window.DeshiMart.searchByHashtag(this.getAttribute(\'data-tag\'))">#তিলের_তেল</span>' +
                               '    <span class="wd-search-sugg-chip" data-tag="চা" onclick="window.DeshiMart.searchByHashtag(this.getAttribute(\'data-tag\'))">#মোরিঙ্গা_চা</span>' +
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
          var qRegex = new RegExp('(' + query.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&') + ')', 'gi');
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
        hashtagsHtml += '<span class="wd-pd-hashtag-pill" data-tag="' + h + '" onclick="window.DeshiMart.searchByHashtag(this.getAttribute(\'data-tag\'))">' + h + '</span>';
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
                       '      <span style="display:inline-block; margin-left:8px; color:#16a34a; font-size:12px; font-weight:600;">ভেরিফাইড ক্রেতা</span>' +
                       '    </div>' +
                       '    <span class="wd-pd-review-date">' + rev.date + '</span>' +
                       '  </div>' +
                       '  <div style="color:#f59e0b; font-size:13px; margin-bottom:6px;"><span class="star-rating">&#9733;&#9733;&#9733;&#9733;&#9733;</span></div>' +
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
      '<a href="javascript:void(0)" data-slug="' + product.category + '" onclick="window.DeshiMart.scrollToCategory(this.getAttribute(\'data-slug\')); return false;">' + (product.categoryName || product.category) + '</a> / ' +
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
      '      <span class="wd-pd-stars"><span class="star-rating">&#9733;&#9733;&#9733;&#9733;&#9733;</span></span>' +
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
      '    <button type="button" class="wd-pd-tab-btn active" data-tab="desc" onclick="window.DeshiMart.switchProductTab(this.getAttribute(\'data-tab\'), this)">বিস্তারিত বিবরণ</button>' +
      '    <button type="button" class="wd-pd-tab-btn" data-tab="nutrition" onclick="window.DeshiMart.switchProductTab(this.getAttribute(\'data-tab\'), this)">পুষ্টিগুণ ও উপাদান</button>' +
      '    <button type="button" class="wd-pd-tab-btn" data-tab="specs" onclick="window.DeshiMart.switchProductTab(this.getAttribute(\'data-tab\'), this)">স্পেসিফিকেশন</button>' +
      '    <button type="button" class="wd-pd-tab-btn" data-tab="hashtags" onclick="window.DeshiMart.switchProductTab(this.getAttribute(\'data-tab\'), this)">হ্যাশট্যাগ ও কিওয়ার্ডস</button>' +
      '    <button type="button" class="wd-pd-tab-btn" data-tab="reviews" onclick="window.DeshiMart.switchProductTab(this.getAttribute(\'data-tab\'), this)">কাস্টমার রিভিউ (' + (product.reviews ? product.reviews.length : 0) + ')</button>' +
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
        btn.innerHTML = 'কার্টে যোগ হয়েছে';

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
  var appliedCoupon = localStorage.getItem('deshi_mart_coupon') || null;

  function applyCoupon() {
    var input = document.getElementById('wd-cart-coupon-input');
    if (!input) return;
    var val = input.value.trim().toUpperCase();
    if (!val) {
      alert('অনুগ্রহ করে কুপন কোড লিখুন।');
      return;
    }
    if (val === 'DESHI10' || val === 'DESHI20' || val === 'FREESHIP' || val === 'SALE10') {
      appliedCoupon = val;
      localStorage.setItem('deshi_mart_coupon', appliedCoupon);
      renderSideCart();
      if (typeof renderCheckoutReviewTable === 'function') renderCheckoutReviewTable();
    } else {
      alert('দুঃখিত, এই কুপন কোডটি সঠিক নয়! আপনি "DESHI10" ব্যবহার করতে পারেন।');
    }
  }

  function removeCoupon() {
    appliedCoupon = null;
    localStorage.removeItem('deshi_mart_coupon');
    renderSideCart();
    if (typeof renderCheckoutReviewTable === 'function') renderCheckoutReviewTable();
  }

  function openCartDrawer() {
    renderSideCart();
    var drawer = document.querySelector('.cart-widget-side');
    var backdrop = document.querySelector('.wd-close-side');
    if (drawer) drawer.classList.add('wd-opened');
    if (backdrop) backdrop.classList.add('wd-close-side-opened');
    document.body.classList.add('wd-close-side-opened');
  }

  function closeCartDrawer() {
    var drawer = document.querySelector('.cart-widget-side');
    var backdrop = document.querySelector('.wd-close-side');
    if (drawer) drawer.classList.remove('wd-opened');
    if (backdrop) backdrop.classList.remove('wd-close-side-opened');
    document.body.classList.remove('wd-close-side-opened');
  }

  function renderSideCart() {
    var container = document.querySelector('.widget_shopping_cart_content');
    if (!container) return;

    var count = cart.reduce(function (c, item) { return c + item.quantity; }, 0);

    // Update Drawer Heading
    var headingTitle = document.querySelector('.cart-widget-side .wd-heading .title');
    if (headingTitle) {
      headingTitle.textContent = 'শপিং ব্যাগ (' + count + ' টি পণ্য)';
    }
    var closeText = document.querySelector('.cart-widget-side .close-side-widget .wd-action-text');
    if (closeText) {
      closeText.textContent = 'বন্ধ করুন';
    }

    if (cart.length === 0) {
      container.innerHTML = '<div style="padding:60px 25px; text-align:center; color:#64748b;">' +
                            '  <div style="font-size:48px; margin-bottom:14px; opacity:0.35;"><svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/></svg></div>' +
                            '  <h3 style="font-size:17px; font-weight:700; color:#1e293b; margin-bottom:8px;">আপনার শপিং ব্যাগ খালি রয়েছে</h3>' +
                            '  <p style="font-size:13px; color:#64748b; margin-bottom:20px;">আমাদের ফ্রেশ দেশি খাঁটি পণ্য দেখতে কেনাকাটা শুরু করুন।</p>' +
                            '  <button class="wd-cart-btn-checkout" style="max-width:200px; margin:0 auto;" onclick="window.DeshiMart.closeCartDrawer(); window.scrollTo({top:800, behavior:\'smooth\'});">পণ্য দেখুন</button>' +
                            '</div>';
      return;
    }

    var subtotal = getCartSubtotal();
    var discount = 0;
    if (appliedCoupon === 'DESHI10' || appliedCoupon === 'SALE10') {
      discount = Math.round(subtotal * 0.10);
    } else if (appliedCoupon === 'DESHI20') {
      discount = Math.round(subtotal * 0.20);
    }
    var totalAfterDiscount = Math.max(0, subtotal - discount);

    var freeShippingGoal = 1500;
    var remaining = Math.max(0, freeShippingGoal - subtotal);
    var progressPercent = Math.min(100, Math.round((subtotal / freeShippingGoal) * 100));

    // 1. Free Shipping Bar
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

    // 2. Items List
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
                   '  <button type="button" class="wd-cart-item-remove" onclick="window.DeshiMart.removeCartItem(' + index + ')" aria-label="Remove">&times;</button>' +
                   '</div>';
    });

    // 3. Coupon Box
    var couponHtml = '<div class="wd-cart-coupon-box">' +
                     (appliedCoupon ?
                     '  <div class="wd-cart-coupon-applied">' +
                     '    <span>কুপন <strong>' + appliedCoupon + '</strong> সক্রিয় (-৳ ' + discount.toLocaleString() + ')</span>' +
                     '    <button type="button" class="wd-cart-coupon-remove" onclick="window.DeshiMart.removeCoupon()">বাতিল</button>' +
                     '  </div>' :
                     '  <div class="wd-cart-coupon-form">' +
                     '    <input type="text" id="wd-cart-coupon-input" placeholder="কুপন কোড (যেমন: DESHI10)" />' +
                     '    <button type="button" onclick="window.DeshiMart.applyCoupon()">প্রয়োগ</button>' +
                     '  </div>') +
                     '</div>';

    // 4. Footer & Summary
    var footerHtml = '<div class="wd-cart-drawer-footer">' +
                     '  <div class="wd-cart-subtotal-row">' +
                     '    <span>পণ্যের মূল্য:</span>' +
                     '    <span>৳ ' + subtotal.toLocaleString() + '</span>' +
                     '  </div>' +
                     (discount > 0 ?
                     '  <div class="wd-cart-subtotal-row" style="color:#16a34a; font-size:14px;">' +
                     '    <span>কুপন ছাড় (১০%):</span>' +
                     '    <span>- ৳ ' + discount.toLocaleString() + '</span>' +
                     '  </div>' : '') +
                     '  <div class="wd-cart-subtotal-row" style="font-size:17px; margin-top:8px; padding-top:8px; border-top:1px dashed #cbd5e1;">' +
                     '    <span>সর্বমোট:</span>' +
                     '    <span class="wd-cart-subtotal-val">৳ ' + totalAfterDiscount.toLocaleString() + '</span>' +
                     '  </div>' +
                     '  <div class="wd-cart-shipping-note">ডেলিভারি চার্জ চেকআউটে এলাকা অনুযায়ী যোগ হবে (ঢাকা ৳ ৬০ / ঢাকার বাইরে ৳ ১২০)</div>' +
                     '  <button type="button" class="wd-cart-btn-checkout" onclick="window.DeshiMart.openCheckout()">' +
                     '    অর্ডার সম্পন্ন করুন (চেকআউট)' +
                     '  </button>' +
                     '  <button type="button" class="wd-cart-btn-continue" onclick="window.DeshiMart.closeCartDrawer()">' +
                     '    আরও কেনাকাটা করুন' +
                     '  </button>' +
                     '  <div class="wd-cart-trust-badges">' +
                     '    <span>ক্যাশ অন ডেলিভারি</span> • ' +
                     '    <span>১০০% খাঁটি পণ্য</span> • ' +
                     '    <span>দ্রুত হোম ডেলিভারি</span>' +
                     '  </div>' +
                     '</div>';

    container.innerHTML = shippingBarHtml +
                          '<div class="wd-cart-items-scrollable">' +
                          itemsHtml +
                          '</div>' +
                          couponHtml +
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

  // --- WoodMart Checkout Modal (Layout 1010) ---
  function openCheckout() {
    closeCartDrawer();
    closeQuickView();

    if (cart.length === 0) {
      alert('আপনার শピング কার্ট খালি! অনুগ্রহ করে প্রথমে একটি পণ্য যুক্ত করুন।');
      return;
    }

    renderCheckout();
    var backdrop = document.getElementById('wd-checkout-backdrop');
    var modal = document.getElementById('wd-checkout-modal');
    if (backdrop) backdrop.classList.add('is-open');
    if (modal) modal.classList.add('is-open');
  }

  function closeCheckout() {
    var backdrop = document.getElementById('wd-checkout-backdrop');
    var modal = document.getElementById('wd-checkout-modal');
    if (backdrop) backdrop.classList.remove('is-open');
    if (modal) modal.classList.remove('is-open');
  }

  function setDeliveryZone(zone) {
    selectedDeliveryZone = zone;
    renderCheckoutReviewTable();
  }

  function renderCheckout() {
    var container = document.getElementById('wd-checkout-content');
    if (!container) return;

    var tpl = document.getElementById('template-layout-1010');
    if (!tpl) return;

    container.innerHTML = tpl.innerHTML;
    var root = container.querySelector('.elementor-1010') || container;

    // Heading in Bangla
    var heading = root.querySelector('.elementor-heading-title');
    if (heading) {
      heading.textContent = 'অর্ডারটি সম্পন্ন করতে আপনার তথ্য প্রদান করুন';
    }

    // Billing Title
    var billingTitle = root.querySelector('.woocommerce-billing-fields h3');
    if (billingTitle) {
      billingTitle.textContent = 'বিলিং ও ডেলিভারি তথ্য';
    }

    // Wrap in interactive form
    var form = root.querySelector('form') || root.querySelector('.woocommerce-billing-fields');
    var placeOrderBtn = root.querySelector('#place_order');
    if (placeOrderBtn) {
      placeOrderBtn.textContent = 'অর্ডার কনফার্ম করুন';
      placeOrderBtn.onclick = function (e) {
        e.preventDefault();
        submitOrder();
      };
    }

    // Payment method switcher
    var paymentRadios = root.querySelectorAll('input[name="payment_method"]');
    paymentRadios.forEach(function (radio) {
      radio.onchange = function () {
        selectedPaymentMethod = radio.value;
        root.querySelectorAll('.payment_box').forEach(function (box) {
          box.style.display = 'none';
        });
        var activeBox = root.querySelector('.payment_box.' + radio.id);
        if (activeBox) activeBox.style.display = 'block';
      };
    });

    renderCheckoutReviewTable();
  }

  function renderCheckoutReviewTable() {
    var modal = document.getElementById('wd-checkout-modal');
    if (!modal) return;

    var subtotal = getCartSubtotal();
    var shippingFee = (selectedDeliveryZone === 'outside') ? 120 : 60;
    
    // Free shipping threshold: ৳ 2,000
    var freeShippingGoal = 2000;
    var isFreeShipping = subtotal >= freeShippingGoal;
    if (isFreeShipping) shippingFee = 0;

    var total = subtotal + shippingFee;

    // 1. Free Shipping Progress Bar
    var progressMsg = modal.querySelector('.wd-free-progress-bar .progress-msg p');
    var progressBar = modal.querySelector('.wd-free-progress-bar .progress-bar');
    if (progressMsg && progressBar) {
      if (isFreeShipping) {
        progressMsg.innerHTML = '<span style="color:#16a34a; font-weight:700;">অভিনন্দন! আপনি ফ্রি শিপিং উপভোগ করছেন!</span>';
        progressBar.style.width = '100%';
        progressBar.style.backgroundColor = '#16a34a';
      } else {
        var remain = freeShippingGoal - subtotal;
        var pct = Math.min(100, Math.round((subtotal / freeShippingGoal) * 100));
        progressMsg.innerHTML = 'কার্টে আরও <span class="amount"><bdi><span class="woocommerce-Price-currencySymbol">৳ </span>' + remain.toLocaleString() + '</bdi></span> টাকার পণ্য যোগ করে ফ্রি শিপিং উপভোগ করুন!';
        progressBar.style.width = pct + '%';
        progressBar.style.backgroundColor = 'var(--wd-primary-color)';
      }
    }

    // 2. Review Table Items
    var tbody = modal.querySelector('.woocommerce-checkout-review-order-table tbody');
    if (tbody) {
      var rowsHtml = '';
      cart.forEach(function (item) {
        rowsHtml += '<tr class="cart_item" style="border-bottom:1px solid #f1f5f9;">' +
                    '  <td class="product-name" style="padding:10px 0; display:flex; align-items:center; gap:10px;">' +
                    '    <img src="' + item.image + '" style="width:40px; height:40px; object-fit:contain; border-radius:4px; border:1px solid #e2e8f0;" />' +
                    '    <div>' +
                    '      <div style="font-weight:600; font-size:13px; color:#1e293b;">' + item.title + '</div>' +
                    '      <div style="font-size:12px; color:#64748b;">' + item.variationName + ' × ' + item.quantity + '</div>' +
                    '    </div>' +
                    '  </td>' +
                    '  <td class="product-total" style="text-align:right; font-weight:700; color:#1e293b; font-size:13px; vertical-align:middle;">' +
                    '    <span class="amount"><bdi><span class="woocommerce-Price-currencySymbol">৳ </span>' + (item.price * item.quantity).toLocaleString() + '</bdi></span>' +
                    '  </td>' +
                    '</tr>';
      });
      tbody.innerHTML = rowsHtml;
    }

    // 3. Shipping Options in Review Table
    var shippingTd = modal.querySelector('.woocommerce-checkout-review-order-table tr.shipping td, .woocommerce-checkout-review-order-table .woocommerce-shipping-totals td');
    if (shippingTd) {
      if (isFreeShipping) {
        shippingTd.innerHTML = '<span style="color:#16a34a; font-weight:700;">ফ্রি শিপিং (৳ 0)</span>';
      } else {
        shippingTd.innerHTML = '<ul id="shipping_method" style="list-style:none; padding:0; margin:0;">' +
                               '  <li style="margin-bottom:6px;">' +
                               '    <label style="cursor:pointer; font-size:13px; display:flex; align-items:center; gap:6px;">' +
                               '      <input type="radio" name="shipping_method_radio" value="dhaka" ' + (selectedDeliveryZone === 'dhaka' ? 'checked' : '') + ' onchange="window.DeshiMart.setDeliveryZone(\'dhaka\')" /> ঢাকা সিটির ভিতরে: ৳ ৬০' +
                               '    </label>' +
                               '  </li>' +
                               '  <li>' +
                               '    <label style="cursor:pointer; font-size:13px; display:flex; align-items:center; gap:6px;">' +
                               '      <input type="radio" name="shipping_method_radio" value="outside" ' + (selectedDeliveryZone === 'outside' ? 'checked' : '') + ' onchange="window.DeshiMart.setDeliveryZone(\'outside\')" /> ঢাকা সিটির বাইরে: ৳ ১২০' +
                               '    </label>' +
                               '  </li>' +
                               '</ul>';
      }
    }

    // 4. Subtotal & Grand Total
    var subtotalAmount = modal.querySelector('.woocommerce-checkout-review-order-table tr.cart-subtotal .amount');
    if (subtotalAmount) {
      subtotalAmount.innerHTML = '<bdi><span class="woocommerce-Price-currencySymbol">৳ </span>' + subtotal.toLocaleString() + '</bdi>';
    }

    var totalAmount = modal.querySelector('.woocommerce-checkout-review-order-table tr.order-total .amount');
    if (totalAmount) {
      totalAmount.innerHTML = '<bdi><span class="woocommerce-Price-currencySymbol">৳ </span>' + total.toLocaleString() + '</bdi>';
    }

    // 5. Update amount in payment instructions (bKash/Nagad/Rocket)
    modal.querySelectorAll('.bdpg-total-amount b').forEach(function (b) {
      b.textContent = '৳ ' + total.toLocaleString();
    });
  }

  function submitOrder() {
    var modal = document.getElementById('wd-checkout-modal');
    if (!modal) return;

    var nameInput = modal.querySelector('#billing_first_name');
    var phoneInput = modal.querySelector('#billing_phone');
    var addressInput = modal.querySelector('#billing_address_1');
    var stateSelect = modal.querySelector('#billing_state');
    var cityInput = modal.querySelector('#billing_city');
    var notesInput = modal.querySelector('#order_comments');

    var name = nameInput ? nameInput.value.trim() : '';
    var phone = phoneInput ? phoneInput.value.trim() : '';
    var address = addressInput ? addressInput.value.trim() : '';
    var district = stateSelect && stateSelect.selectedOptions[0] ? stateSelect.selectedOptions[0].text : 'Dhaka';
    var thana = cityInput ? cityInput.value.trim() : '';
    var notes = notesInput ? notesInput.value.trim() : '';

    if (!name) {
      alert('অনুগ্রহ করে আপনার নাম লিখুন।');
      if (nameInput) nameInput.focus();
      return;
    }

    var phoneRegex = /^01[3-9]\d{8}$/;
    if (!phoneRegex.test(phone.replace(/[- ]/g, ''))) {
      alert('অনুগ্রহ করে সঠিক ১১ ডিজিটের মোবাইল নম্বর দিন (যেমন: 017XXXXXXXX)।');
      if (phoneInput) phoneInput.focus();
      return;
    }

    if (!address) {
      alert('অনুগ্রহ করে আপনার সম্পূর্ণ ডেলিভারি ঠিকানা দিন।');
      if (addressInput) addressInput.focus();
      return;
    }

    var submitBtn = modal.querySelector('#place_order');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'অর্ডার প্রসেস হচ্ছে...';
    }

    setTimeout(function () {
      var subtotal = getCartSubtotal();
      var shippingFee = (selectedDeliveryZone === 'outside') ? 120 : 60;
      if (subtotal >= 2000) shippingFee = 0;
      var total = subtotal + shippingFee;
      var orderId = 'DM-' + Math.floor(100000 + Math.random() * 900000);

      var paymentMethodTitle = 'ক্যাশ অন ডেলিভারি (Cash on Delivery)';
      if (selectedPaymentMethod === 'woo_bkash') paymentMethodTitle = 'bKash';
      else if (selectedPaymentMethod === 'woo_nagad') paymentMethodTitle = 'Nagad';
      else if (selectedPaymentMethod === 'woo_rocket') paymentMethodTitle = 'Rocket';
      else if (selectedPaymentMethod === 'woo_upay') paymentMethodTitle = 'Upay';

      var invoiceDetails = '<div style="margin-bottom:8px;"><strong>অর্ডার ট্র্যাকিং আইডি:</strong> #' + orderId + '</div>' +
                           '<div style="margin-bottom:8px;"><strong>গ্রাহকের নাম:</strong> ' + name + '</div>' +
                           '<div style="margin-bottom:8px;"><strong>মোবাইল নাম্বার:</strong> ' + phone + '</div>' +
                           '<div style="margin-bottom:8px;"><strong>ডেলিভারি ঠিকানা:</strong> ' + address + (thana ? ', ' + thana : '') + ', ' + district + '</div>' +
                           '<div style="margin-bottom:8px;"><strong>ডেলিভারি এলাকা:</strong> ' + (selectedDeliveryZone === 'outside' ? 'ঢাকা সিটির বাইরে (৳ ১২০)' : 'ঢাকা সিটির ভিতরে (৳ ৬০)') + (shippingFee === 0 ? ' [ফ্রি শিপিং]' : '') + '</div>' +
                           '<div style="margin-bottom:8px;"><strong>পেমেন্ট পদ্ধতি:</strong> ' + paymentMethodTitle + '</div>' +
                           (notes ? '<div style="margin-bottom:8px;"><strong>অর্ডার নোট:</strong> ' + notes + '</div>' : '') +
                           '<div style="margin-top:12px; padding-top:8px; border-top:1px dashed #cbd5e1; font-weight:700; color:var(--wd-primary-color); font-size:15px;">' +
                           '  সর্বমোট প্রদেয় মূল্য: ৳ ' + total.toLocaleString() +
                           '</div>';

      var invoiceBox = document.getElementById('wd-order-invoice-details');
      if (invoiceBox) invoiceBox.innerHTML = invoiceDetails;

      closeCheckout();

      var successModal = document.getElementById('wd-order-success-modal');
      if (successModal) successModal.classList.add('is-open');

      // Clear cart
      cart = [];
      saveCart();
    }, 600);
  }

  function closeOrderSuccess() {
    var successModal = document.getElementById('wd-order-success-modal');
    if (successModal) successModal.classList.remove('is-open');
  }

  // --- Category Smooth Scrolling ---
  function filterCategory(slug, btn) {
    slug = (slug || 'all').toLowerCase().trim();

    // 1. Update filter tab buttons active state
    var buttons = document.querySelectorAll('.wd-category-filter-btn');
    buttons.forEach(function (b) {
      if (b.getAttribute('data-cat') === slug) {
        b.classList.add('active');
      } else {
        b.classList.remove('active');
      }
    });

    // 2. Filter products in All Products section
    var headings = document.querySelectorAll('.elementor-heading-title');
    var allProductsHeading = null;
    headings.forEach(function (h) {
      if (h.textContent.trim().indexOf('All Products') !== -1) {
        allProductsHeading = h;
      }
    });

    var grid = null;
    if (allProductsHeading) {
      var container = allProductsHeading.closest('.elementor-element');
      while (container && !grid) {
        grid = container.querySelector('.products');
        container = container.parentElement;
      }
    }
    if (!grid) {
      grid = document.querySelector('.products.grid-columns-5') || document.querySelector('.wd-products.elements-grid');
    }

    if (grid) {
      var cards = grid.querySelectorAll('.wd-product');
      cards.forEach(function (card) {
        var cardCat = card.getAttribute('data-category') || '';
        if (slug === 'all' || cardCat === slug) {
          card.classList.remove('wd-cat-hidden');
          card.classList.add('wd-cat-visible');
        } else {
          card.classList.add('wd-cat-hidden');
          card.classList.remove('wd-cat-visible');
        }
      });
    }
  }

  function scrollToCategory(slug) {
    slug = (slug || '').toLowerCase().trim();

    var headings = document.querySelectorAll('.elementor-heading-title');
    var targetEl = null;

    if (slug === 'ghee') {
      headings.forEach(function (h) {
        if (h.textContent.trim().indexOf('All Homemade Ghee') !== -1) targetEl = h;
      });
    } else if (slug === 'dates' || slug === 'honey') {
      headings.forEach(function (h) {
        if (h.textContent.trim().indexOf('All Honey/Dates') !== -1) targetEl = h;
      });
    } else if (slug === 'oil' || slug === 'exclusive') {
      headings.forEach(function (h) {
        if (h.textContent.trim().indexOf('All Exclusive Products') !== -1) targetEl = h;
      });
    } else {
      // tea, nuts, spices, shutki, all
      headings.forEach(function (h) {
        if (h.textContent.trim().indexOf('All Products') !== -1) targetEl = h;
      });
      // Activate that category tab in All Products
      filterCategory(slug);
    }

    if (!targetEl) {
      headings.forEach(function (h) {
        if (h.textContent.trim().indexOf('All Products') !== -1) targetEl = h;
      });
    }

    if (targetEl) {
      var top = targetEl.getBoundingClientRect().top + window.pageYOffset - 90;
      window.scrollTo({ top: top, behavior: 'smooth' });
    }
  }

  // --- Attach Global Listeners on DOM Ready ---
  function addProductToCartFromCard(pid, btn) {
    var product = getProduct(pid);
    if (!product) return;

    var curVar = product.variations[0];
    if (btn) {
      var origText = btn.innerHTML;
      btn.innerHTML = 'যোগ হচ্ছে...';
      btn.disabled = true;

      setTimeout(function () {
        btn.classList.add('btn-added-success');
        btn.innerHTML = 'কার্টে যোগ হয়েছে';

        setTimeout(function () {
          btn.classList.remove('btn-added-success');
          btn.innerHTML = origText;
          btn.disabled = false;
        }, 1200);
      }, 200);
    }

    var existing = cart.find(function (item) {
      return item.productId === product.id && item.variationName === curVar.name;
    });

    if (existing) {
      existing.quantity += 1;
    } else {
      cart.push({
        productId: product.id,
        title: product.title,
        variationName: curVar.name,
        price: curVar.price,
        image: product.images[0],
        quantity: 1
      });
    }

    saveCart();
    triggerCartBadgeBounce();

    setTimeout(function () {
      openCartDrawer();
    }, 350);
  }

  function initCardBindings() {
    // Intercept clicks on product links or buttons
    document.querySelectorAll('.wd-product').forEach(function (card) {
      var pid = parseInt(card.getAttribute('data-id'), 10);
      if (!pid) return;

      var openDetailHandler = function (e) {
        e.preventDefault();
        e.stopPropagation();
        openQuickView(pid);
      };

      // Direct Add to Cart from card
      var atcBtn = card.querySelector('.add_to_cart_button');
      if (atcBtn) {
        atcBtn.onclick = function (e) {
          e.preventDefault();
          e.stopPropagation();
          addProductToCartFromCard(pid, atcBtn);
        };
      }

      // Quick view icon link opens full details
      var qvBtn = card.querySelector('.open-quick-view');
      if (qvBtn) qvBtn.onclick = openDetailHandler;

      // Product image link opens full details
      var imgLink = card.querySelector('.wd-product-img-link');
      if (imgLink) imgLink.onclick = openDetailHandler;

      // Product title link opens full details
      var titleLink = card.querySelector('.wd-loop-prod-title a');
      if (titleLink) titleLink.onclick = openDetailHandler;

      // Buy Now button
      var buyBtn = card.querySelector('.isl-loop-buy-now');
      if (buyBtn) {
        buyBtn.onclick = function (e) {
          e.preventDefault();
          e.stopPropagation();
          quickBuyNow(pid);
        };
      }
    });

    // Cart openers (desktop header, sticky header, mobile toolbar)
    document.querySelectorAll('.cart-widget-opener, .wd-header-cart, .wd-toolbar-cart').forEach(function (opener) {
      opener.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        openCartDrawer();
      });
    });

    // Close side drawer backdrop
    var backdropClose = document.querySelector('.wd-close-side');
    if (backdropClose) {
      backdropClose.onclick = closeCartDrawer;
    }

    var sideCloseBtn = document.querySelector('.close-side-widget a');
    if (sideCloseBtn) {
      sideCloseBtn.onclick = function (e) {
        e.preventDefault();
        closeCartDrawer();
      };
    }
  }

  // Export to window
  window.DeshiMart = {
    applyCoupon: applyCoupon,
    removeCoupon: removeCoupon,
    openQuickView: openQuickView,
    closeQuickView: closeQuickView,
    switchProductTab: switchProductTab,
    searchByHashtag: searchByHashtag,
    selectVariation: selectVariation,
    setGalleryImage: setGalleryImage,
    changeQuickViewQty: changeQuickViewQty,
    addToCartFromQuickView: addToCartFromQuickView,
    addProductToCartFromCard: addProductToCartFromCard,
    buyNowFromQuickView: buyNowFromQuickView,
    quickBuyNow: quickBuyNow,
    openCartDrawer: openCartDrawer,
    closeCartDrawer: closeCartDrawer,
    updateCartQty: updateCartQty,
    removeCartItem: removeCartItem,
    openCheckout: openCheckout,
    closeCheckout: closeCheckout,
    setDeliveryZone: setDeliveryZone,
    submitOrder: submitOrder,
    closeOrderSuccess: closeOrderSuccess,
    scrollToCategory: scrollToCategory,
    filterCategory: filterCategory
  };

  document.addEventListener('DOMContentLoaded', function () {
    updateCartBadges();
    // Native WoodMart slider handles slider-28 and slider-32 via Swiper
    // initHeroSliders();
    initBrandCarousel();
    initScrollAnimations();
    initStickyHeader();
    initInstantSearch();
    initCardBindings();

    // Support deep-linking for quickview & cart
    var urlParams = new URLSearchParams(window.location.search);
    var qvParam = urlParams.get('quickview') || urlParams.get('product');
    var addCartParam = urlParams.get('add_cart');
    var sampleCartParam = urlParams.get('sample_cart');
    var searchParam = urlParams.get('search');

    if (sampleCartParam) {
      cart = [
        {
          productId: 533,
          title: "ACME প্রিমিয়াম বিশুদ্ধ ঘি",
          variationName: "200 Gram",
          price: 350,
          image: "./wp-content/uploads/2026/08/1-2-1-1.webp",
          quantity: 1
        },
        {
          productId: 530,
          title: "অর্গানিক ফ্রেশ কালমি খেজুর",
          variationName: "500 Gram",
          price: 850,
          image: "./wp-content/uploads/2026/08/kalmi-dates-khejur-500-gm.webp",
          quantity: 1
        },
        {
          productId: 528,
          title: "কারকুমা অর্গানিক বিশুদ্ধ মধু",
          variationName: "500 Gram",
          price: 300,
          image: "./wp-content/uploads/2026/08/karkuma.webp",
          quantity: 1
        }
      ];
      saveCart();
      if (urlParams.get('checkout') === '1') {
        setTimeout(function () {
          openCheckout();
        }, 350);
      } else {
        setTimeout(function () {
          openCartDrawer();
        }, 350);
      }
    } else if (searchParam) {
      setTimeout(function () {
        var sInput = document.querySelector('.searchform input[type="text"], .searchform input[name="s"]');
        if (sInput) {
          sInput.value = searchParam;
          sInput.focus();
          sInput.dispatchEvent(new Event('input'));
        }
      }, 300);
    } else if (addCartParam) {
      setTimeout(function () {
        addProductToCartFromCard(parseInt(addCartParam, 10));
      }, 300);
    } else if (qvParam) {
      setTimeout(function () {
        openQuickView(parseInt(qvParam, 10) || qvParam);
        var tabParam = urlParams.get('tab');
        if (tabParam) {
          setTimeout(function () {
            var tabBtn = document.querySelector('.wd-pd-tab-btn[data-tab="' + tabParam + '"]');
            switchProductTab(tabParam, tabBtn);
          }, 350);
        }
        var scrollVal = urlParams.get('scroll');
        if (scrollVal) {
          setTimeout(function () {
            var pop = document.querySelector('.wd-product-detail-container');
            if (pop) pop.scrollTop = parseInt(scrollVal, 10);
          }, 450);
        }
      }, 300);
    } else if (urlParams.get('cart') === 'open' || urlParams.get('cart') === '1') {
      setTimeout(function () {
        openCartDrawer();
      }, 300);
    }
  });
})();
