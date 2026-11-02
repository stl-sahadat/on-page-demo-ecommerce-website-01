# -*- coding: utf-8 -*-
with open('js/app.js', 'r', encoding='utf-8') as f:
    code = f.read()

pos1 = code.find('  // --- Side Cart Drawer (Authentic WoodMart Experience) ---')
pos2 = code.find('  // --- WoodMart Checkout Modal (Layout 1010) ---')

new_cart_code = '''  // --- Side Cart Drawer (Authentic WoodMart Experience) ---
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
                            '  <div style="font-size:48px; margin-bottom:14px; opacity:0.35;">🛒</div>' +
                            '  <h3 style="font-size:17px; font-weight:700; color:#1e293b; margin-bottom:8px;">আপনার শপিং ব্যাগ খালি রয়েছে</h3>' +
                            '  <p style="font-size:13px; color:#64748b; margin-bottom:20px;">আমাদের ফ্রেশ দেশি খাঁটি পণ্য দেখতে কেনাকাটা শুরু করুন।</p>' +
                            '  <button class="wd-cart-btn-checkout" style="max-width:200px; margin:0 auto;" onclick="window.DeshiMart.closeCartDrawer(); window.scrollTo({top:800, behavior:\\'smooth\\'});">পণ্য দেখুন</button>' +
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
                   '  <button type="button" class="wd-cart-item-remove" onclick="window.DeshiMart.removeCartItem(' + index + ')" aria-label="Remove">✕</button>' +
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
\n'''

code = code[:pos1] + new_cart_code + code[pos2:]

# Also export applyCoupon and removeCoupon
pos_exp = code.find('window.DeshiMart = {')
if pos_exp != -1:
    code = code.replace(
        'window.DeshiMart = {',
        'window.DeshiMart = {\n    applyCoupon: applyCoupon,\n    removeCoupon: removeCoupon,'
    )

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated app.js cart engine successfully!")
