fetch('https://jsonplaceholder.typicode.com/posts/1')
  .then(res => res.json())
  .then(console.log)

fetch('https://www.supremenewyork.com/mobile_stock.json')
  .then(res => res.json())
  .then(console.log)

  ###

  ;(function () {
  'use strict';

  /**
   * @preserve FastClick: polyfill to remove click delays on browsers with touch UIs.
   *
   * @codingstandard ftlabs-jsv2
   * @copyright The Financial Times Limited [All Rights Reserved]
   * @license MIT License (see LICENSE.txt)
   */

  /*jslint browser:true, node:true*/
  /*global define, Event, Node*/


  /**
   * Instantiate fast-clicking listeners on the specified layer.
   *
   * @constructor
   * @param {Element} layer The layer to listen on
   * @param {Object} [options={}] The options to override the defaults
   */
  function FastClick(layer, options) {
    var oldOnClick;

    options = options || {};

    /**
     * Whether a click is currently being tracked.
     *
     * @type boolean
     */
    this.trackingClick = false;


    /**
     * Timestamp for when click tracking started.
     *
     * @type number
     */
    this.trackingClickStart = 0;


    /**
     * The element being tracked for a click.
     *
     * @type EventTarget
     */
    this.targetElement = null;


    /**
     * X-coordinate of touch start event.
     *
     * @type number
     */
    this.touchStartX = 0;


    /**
     * Y-coordinate of touch start event.
     *
     * @type number
     */
    this.touchStartY = 0;


    /**
     * ID of the last touch, retrieved from Touch.identifier.
     *
     * @type number
     */
    this.lastTouchIdentifier = 0;


    /**
     * Touchmove boundary, beyond which a click will be cancelled.
     *
     * @type number
     */
    this.touchBoundary = options.touchBoundary || 10;


    /**
     * The FastClick layer.
     *
     * @type Element
     */
    this.layer = layer;

    /**
     * The minimum time between tap(touchstart and touchend) events
     *
     * @type number
     */
    this.tapDelay = options.tapDelay || 200;

    /**
     * The maximum time for a tap
     *
     * @type number
     */
    this.tapTimeout = options.tapTimeout || 700;

    if (FastClick.notNeeded(layer)) {
      return;
    }

    // Some old versions of Android don't have Function.prototype.bind
    function bind(method, context) {
      return function() { return method.apply(context, arguments); };
    }


    var methods = ['onMouse', 'onClick', 'onTouchStart', 'onTouchMove', 'onTouchEnd', 'onTouchCancel'];
    var context = this;
    for (var i = 0, l = methods.length; i < l; i++) {
      context[methods[i]] = bind(context[methods[i]], context);
    }

    // Set up event handlers as required
    if (deviceIsAndroid) {
      layer.addEventListener('mouseover', this.onMouse, true);
      layer.addEventListener('mousedown', this.onMouse, true);
      layer.addEventListener('mouseup', this.onMouse, true);
    }

    layer.addEventListener('click', this.onClick, true);
    layer.addEventListener('touchstart', this.onTouchStart, false);
    layer.addEventListener('touchmove', this.onTouchMove, false);
    layer.addEventListener('touchend', this.onTouchEnd, false);
    layer.addEventListener('touchcancel', this.onTouchCancel, false);

    // Hack is required for browsers that don't support Event#stopImmediatePropagation (e.g. Android 2)
    // which is how FastClick normally stops click events bubbling to callbacks registered on the FastClick
    // layer when they are cancelled.
    if (!Event.prototype.stopImmediatePropagation) {
      layer.removeEventListener = function(type, callback, capture) {
        var rmv = Node.prototype.removeEventListener;
        if (type === 'click') {
          rmv.call(layer, type, callback.hijacked || callback, capture);
        } else {
          rmv.call(layer, type, callback, capture);
        }
      };

      layer.addEventListener = function(type, callback, capture) {
        var adv = Node.prototype.addEventListener;
        if (type === 'click') {
          adv.call(layer, type, callback.hijacked || (callback.hijacked = function(event) {
            if (!event.propagationStopped) {
              callback(event);
            }
          }), capture);
        } else {
          adv.call(layer, type, callback, capture);
        }
      };
    }

    // If a handler is already declared in the element's onclick attribute, it will be fired before
    // FastClick's onClick handler. Fix this by pulling out the user-defined handler function and
    // adding it as listener.
    if (typeof layer.onclick === 'function') {

      // Android browser on at least 3.2 requires a new reference to the function in layer.onclick
      // - the old one won't work if passed to addEventListener directly.
      oldOnClick = layer.onclick;
      layer.addEventListener('click', function(event) {
        oldOnClick(event);
      }, false);
      layer.onclick = null;
    }
  }

  /**
  * Windows Phone 8.1 fakes user agent string to look like Android and iPhone.
  *
  * @type boolean
  */
  var deviceIsWindowsPhone = navigator.userAgent.indexOf("Windows Phone") >= 0;

  /**
   * Android requires exceptions.
   *
   * @type boolean
   */
  var deviceIsAndroid = navigator.userAgent.indexOf('Android') > 0 && !deviceIsWindowsPhone;


  /**
   * iOS requires exceptions.
   *
   * @type boolean
   */
  var deviceIsIOS = /iP(ad|hone|od)/.test(navigator.userAgent) && !deviceIsWindowsPhone;


  /**
   * iOS 4 requires an exception for select elements.
   *
   * @type boolean
   */
  var deviceIsIOS4 = deviceIsIOS && (/OS 4_\d(_\d)?/).test(navigator.userAgent);


  /**
   * iOS 6.0-7.* requires the target element to be manually derived
   *
   * @type boolean
   */
  var deviceIsIOSWithBadTarget = deviceIsIOS && (/OS [6-7]_\d/).test(navigator.userAgent);

  /**
   * BlackBerry requires exceptions.
   *
   * @type boolean
   */
  var deviceIsBlackBerry10 = navigator.userAgent.indexOf('BB10') > 0;

  /**
   * Determine whether a given element requires a native click.
   *
   * @param {EventTarget|Element} target Target DOM element
   * @returns {boolean} Returns true if the element needs a native click
   */
  FastClick.prototype.needsClick = function(target) {
    switch (target.nodeName.toLowerCase()) {

    // Don't send a synthetic click to disabled inputs (issue #62)
    case 'button':
    case 'select':
    case 'textarea':
      if (target.disabled) {
        return true;
      }

      break;
    case 'input':

      // File inputs need real clicks on iOS 6 due to a browser bug (issue #68)
      if ((deviceIsIOS && target.type === 'file') || target.disabled) {
        return true;
      }

      break;
    case 'label':
    case 'iframe': // iOS8 homescreen apps can prevent events bubbling into frames
    case 'video':
      return true;
    }

    return (/\bneedsclick\b/).test(target.className);
  };


  /**
   * Determine whether a given element requires a call to focus to simulate click into element.
   *
   * @param {EventTarget|Element} target Target DOM element
   * @returns {boolean} Returns true if the element requires a call to focus to simulate native click.
   */
  FastClick.prototype.needsFocus = function(target) {
    switch (target.nodeName.toLowerCase()) {
    case 'textarea':
      return true;
    case 'select':
      return !deviceIsAndroid;
    case 'input':
      switch (target.type) {
      case 'button':
      case 'checkbox':
      case 'file':
      case 'image':
      case 'radio':
      case 'submit':
        return false;
      }

      // No point in attempting to focus disabled inputs
      return !target.disabled && !target.readOnly;
    default:
      return (/\bneedsfocus\b/).test(target.className);
    }
  };


  /**
   * Send a click event to the specified element.
   *
   * @param {EventTarget|Element} targetElement
   * @param {Event} event
   */
  FastClick.prototype.sendClick = function(targetElement, event) {
    var clickEvent, touch;

    // On some Android devices activeElement needs to be blurred otherwise the synthetic click will have no effect (#24)
    if (document.activeElement && document.activeElement !== targetElement) {
      document.activeElement.blur();
    }

    touch = event.changedTouches[0];

    // Synthesise a click event, with an extra attribute so it can be tracked
    clickEvent = document.createEvent('MouseEvents');
    clickEvent.initMouseEvent(this.determineEventType(targetElement), true, true, window, 1, touch.screenX, touch.screenY, touch.clientX, touch.clientY, false, false, false, false, 0, null);
    clickEvent.forwardedTouchEvent = true;
    targetElement.dispatchEvent(clickEvent);
  };

  FastClick.prototype.determineEventType = function(targetElement) {

    //Issue #159: Android Chrome Select Box does not open with a synthetic click event
    if (deviceIsAndroid && targetElement.tagName.toLowerCase() === 'select') {
      return 'mousedown';
    }

    return 'click';
  };


  /**
   * @param {EventTarget|Element} targetElement
   */
  FastClick.prototype.focus = function(targetElement) {
    var length;

    // Issue #160: on iOS 7, some input elements (e.g. date datetime month) throw a vague TypeError on setSelectionRange. These elements don't have an integer value for the selectionStart and selectionEnd properties, but unfortunately that can't be used for detection because accessing the properties also throws a TypeError. Just check the type instead. Filed as Apple bug #15122724.
    if (deviceIsIOS && targetElement.setSelectionRange && targetElement.type.indexOf('date') !== 0 && targetElement.type !== 'time' && targetElement.type !== 'month') {
      length = targetElement.value.length;
      targetElement.setSelectionRange(length, length);
    } else {
      targetElement.focus();
    }
  };


  /**
   * Check whether the given target element is a child of a scrollable layer and if so, set a flag on it.
   *
   * @param {EventTarget|Element} targetElement
   */
  FastClick.prototype.updateScrollParent = function(targetElement) {
    var scrollParent, parentElement;

    scrollParent = targetElement.fastClickScrollParent;

    // Attempt to discover whether the target element is contained within a scrollable layer. Re-check if the
    // target element was moved to another parent.
    if (!scrollParent || !scrollParent.contains(targetElement)) {
      parentElement = targetElement;
      do {
        if (parentElement.scrollHeight > parentElement.offsetHeight) {
          scrollParent = parentElement;
          targetElement.fastClickScrollParent = parentElement;
          break;
        }

        parentElement = parentElement.parentElement;
      } while (parentElement);
    }

    // Always update the scroll top tracker if possible.
    if (scrollParent) {
      scrollParent.fastClickLastScrollTop = scrollParent.scrollTop;
    }
  };


  /**
   * @param {EventTarget} targetElement
   * @returns {Element|EventTarget}
   */
  FastClick.prototype.getTargetElementFromEventTarget = function(eventTarget) {

    // On some older browsers (notably Safari on iOS 4.1 - see issue #56) the event target may be a text node.
    if (eventTarget.nodeType === Node.TEXT_NODE) {
      return eventTarget.parentNode;
    }

    return eventTarget;
  };


  /**
   * On touch start, record the position and scroll offset.
   *
   * @param {Event} event
   * @returns {boolean}
   */
  FastClick.prototype.onTouchStart = function(event) {
    var targetElement, touch, selection;

    // Ignore multiple touches, otherwise pinch-to-zoom is prevented if both fingers are on the FastClick element (issue #111).
    if (event.targetTouches.length > 1) {
      return true;
    }

    targetElement = this.getTargetElementFromEventTarget(event.target);
    touch = event.targetTouches[0];

    if (deviceIsIOS) {

      // Only trusted events will deselect text on iOS (issue #49)
      selection = window.getSelection();
      if (selection.rangeCount && !selection.isCollapsed) {
        return true;
      }

      if (!deviceIsIOS4) {

        // Weird things happen on iOS when an alert or confirm dialog is opened from a click event callback (issue #23):
        // when the user next taps anywhere else on the page, new touchstart and touchend events are dispatched
        // with the same identifier as the touch event that previously triggered the click that triggered the alert.
        // Sadly, there is an issue on iOS 4 that causes some normal touch events to have the same identifier as an
        // immediately preceeding touch event (issue #52), so this fix is unavailable on that platform.
        // Issue 120: touch.identifier is 0 when Chrome dev tools 'Emulate touch events' is set with an iOS device UA string,
        // which causes all touch events to be ignored. As this block only applies to iOS, and iOS identifiers are always long,
        // random integers, it's safe to to continue if the identifier is 0 here.
        if (touch.identifier && touch.identifier === this.lastTouchIdentifier) {
          event.preventDefault();
          return false;
        }

        this.lastTouchIdentifier = touch.identifier;

        // If the target element is a child of a scrollable layer (using -webkit-overflow-scrolling: touch) and:
        // 1) the user does a fling scroll on the scrollable layer
        // 2) the user stops the fling scroll with another tap
        // then the event.target of the last 'touchend' event will be the element that was under the user's finger
        // when the fling scroll was started, causing FastClick to send a click event to that layer - unless a check
        // is made to ensure that a parent layer was not scrolled before sending a synthetic click (issue #42).
        this.updateScrollParent(targetElement);
      }
    }

    this.trackingClick = true;
    this.trackingClickStart = event.timeStamp;
    this.targetElement = targetElement;

    this.touchStartX = touch.pageX;
    this.touchStartY = touch.pageY;

    // Prevent phantom clicks on fast double-tap (issue #36)
    if ((event.timeStamp - this.lastClickTime) < this.tapDelay) {
      event.preventDefault();
    }

    return true;
  };


  /**
   * Based on a touchmove event object, check whether the touch has moved past a boundary since it started.
   *
   * @param {Event} event
   * @returns {boolean}
   */
  FastClick.prototype.touchHasMoved = function(event) {
    var touch = event.changedTouches[0], boundary = this.touchBoundary;

    if (Math.abs(touch.pageX - this.touchStartX) > boundary || Math.abs(touch.pageY - this.touchStartY) > boundary) {
      return true;
    }

    return false;
  };


  /**
   * Update the last position.
   *
   * @param {Event} event
   * @returns {boolean}
   */
  FastClick.prototype.onTouchMove = function(event) {
    if (!this.trackingClick) {
      return true;
    }

    // If the touch has moved, cancel the click tracking
    if (this.targetElement !== this.getTargetElementFromEventTarget(event.target) || this.touchHasMoved(event)) {
      this.trackingClick = false;
      this.targetElement = null;
    }

    return true;
  };


  /**
   * Attempt to find the labelled control for the given label element.
   *
   * @param {EventTarget|HTMLLabelElement} labelElement
   * @returns {Element|null}
   */
  FastClick.prototype.findControl = function(labelElement) {

    // Fast path for newer browsers supporting the HTML5 control attribute
    if (labelElement.control !== undefined) {
      return labelElement.control;
    }

    // All browsers under test that support touch events also support the HTML5 htmlFor attribute
    if (labelElement.htmlFor) {
      return document.getElementById(labelElement.htmlFor);
    }

    // If no for attribute exists, attempt to retrieve the first labellable descendant element
    // the list of which is defined here: http://www.w3.org/TR/html5/forms.html#category-label
    return labelElement.querySelector('button, input:not([type=hidden]), keygen, meter, output, progress, select, textarea');
  };


  /**
   * On touch end, determine whether to send a click event at once.
   *
   * @param {Event} event
   * @returns {boolean}
   */
  FastClick.prototype.onTouchEnd = function(event) {
    var forElement, trackingClickStart, targetTagName, scrollParent, touch, targetElement = this.targetElement;

    if (!this.trackingClick) {
      return true;
    }

    // Prevent phantom clicks on fast double-tap (issue #36)
    if ((event.timeStamp - this.lastClickTime) < this.tapDelay) {
      this.cancelNextClick = true;
      return true;
    }

    if ((event.timeStamp - this.trackingClickStart) > this.tapTimeout) {
      return true;
    }

    // Reset to prevent wrong click cancel on input (issue #156).
    this.cancelNextClick = false;

    this.lastClickTime = event.timeStamp;

    trackingClickStart = this.trackingClickStart;
    this.trackingClick = false;
    this.trackingClickStart = 0;

    // On some iOS devices, the targetElement supplied with the event is invalid if the layer
    // is performing a transition or scroll, and has to be re-detected manually. Note that
    // for this to function correctly, it must be called *after* the event target is checked!
    // See issue #57; also filed as rdar://13048589 .
    if (deviceIsIOSWithBadTarget) {
      touch = event.changedTouches[0];

      // In certain cases arguments of elementFromPoint can be negative, so prevent setting targetElement to null
      targetElement = document.elementFromPoint(touch.pageX - window.pageXOffset, touch.pageY - window.pageYOffset) || targetElement;
      targetElement.fastClickScrollParent = this.targetElement.fastClickScrollParent;
    }

    targetTagName = targetElement.tagName.toLowerCase();
    if (targetTagName === 'label') {
      forElement = this.findControl(targetElement);
      if (forElement) {
        this.focus(targetElement);
        if (deviceIsAndroid) {
          return false;
        }

        targetElement = forElement;
      }
    } else if (this.needsFocus(targetElement)) {

      // Case 1: If the touch started a while ago (best guess is 100ms based on tests for issue #36) then focus will be triggered anyway. Return early and unset the target element reference so that the subsequent click will be allowed through.
      // Case 2: Without this exception for input elements tapped when the document is contained in an iframe, then any inputted text won't be visible even though the value attribute is updated as the user types (issue #37).
      if ((event.timeStamp - trackingClickStart) > 100 || (deviceIsIOS && window.top !== window && targetTagName === 'input')) {
        this.targetElement = null;
        return false;
      }

      this.focus(targetElement);
      this.sendClick(targetElement, event);

      // Select elements need the event to go through on iOS 4, otherwise the selector menu won't open.
      // Also this breaks opening selects when VoiceOver is active on iOS6, iOS7 (and possibly others)
      if (!deviceIsIOS || targetTagName !== 'select') {
        this.targetElement = null;
        event.preventDefault();
      }

      return false;
    }

    if (deviceIsIOS && !deviceIsIOS4) {

      // Don't send a synthetic click event if the target element is contained within a parent layer that was scrolled
      // and this tap is being used to stop the scrolling (usually initiated by a fling - issue #42).
      scrollParent = targetElement.fastClickScrollParent;
      if (scrollParent && scrollParent.fastClickLastScrollTop !== scrollParent.scrollTop) {
        return true;
      }
    }

    // Prevent the actual click from going though - unless the target node is marked as requiring
    // real clicks or if it is in the whitelist in which case only non-programmatic clicks are permitted.
    if (!this.needsClick(targetElement)) {
      event.preventDefault();
      this.sendClick(targetElement, event);
    }

    return false;
  };


  /**
   * On touch cancel, stop tracking the click.
   *
   * @returns {void}
   */
  FastClick.prototype.onTouchCancel = function() {
    this.trackingClick = false;
    this.targetElement = null;
  };


  /**
   * Determine mouse events which should be permitted.
   *
   * @param {Event} event
   * @returns {boolean}
   */
  FastClick.prototype.onMouse = function(event) {

    // If a target element was never set (because a touch event was never fired) allow the event
    if (!this.targetElement) {
      return true;
    }

    if (event.forwardedTouchEvent) {
      return true;
    }

    // Programmatically generated events targeting a specific element should be permitted
    if (!event.cancelable) {
      return true;
    }

    // Derive and check the target element to see whether the mouse event needs to be permitted;
    // unless explicitly enabled, prevent non-touch click events from triggering actions,
    // to prevent ghost/doubleclicks.
    if (!this.needsClick(this.targetElement) || this.cancelNextClick) {

      // Prevent any user-added listeners declared on FastClick element from being fired.
      if (event.stopImmediatePropagation) {
        event.stopImmediatePropagation();
      } else {

        // Part of the hack for browsers that don't support Event#stopImmediatePropagation (e.g. Android 2)
        event.propagationStopped = true;
      }

      // Cancel the event
      event.stopPropagation();
      event.preventDefault();

      return false;
    }

    // If the mouse event is permitted, return true for the action to go through.
    return true;
  };


  /**
   * On actual clicks, determine whether this is a touch-generated click, a click action occurring
   * naturally after a delay after a touch (which needs to be cancelled to avoid duplication), or
   * an actual click which should be permitted.
   *
   * @param {Event} event
   * @returns {boolean}
   */
  FastClick.prototype.onClick = function(event) {
    var permitted;

    // It's possible for another FastClick-like library delivered with third-party code to fire a click event before FastClick does (issue #44). In that case, set the click-tracking flag back to false and return early. This will cause onTouchEnd to return early.
    if (this.trackingClick) {
      this.targetElement = null;
      this.trackingClick = false;
      return true;
    }

    // Very odd behaviour on iOS (issue #18): if a submit element is present inside a form and the user hits enter in the iOS simulator or clicks the Go button on the pop-up OS keyboard the a kind of 'fake' click event will be triggered with the submit-type input element as the target.
    if (event.target.type === 'submit' && event.detail === 0) {
      return true;
    }

    permitted = this.onMouse(event);

    // Only unset targetElement if the click is not permitted. This will ensure that the check for !targetElement in onMouse fails and the browser's click doesn't go through.
    if (!permitted) {
      this.targetElement = null;
    }

    // If clicks are permitted, return true for the action to go through.
    return permitted;
  };


  /**
   * Remove all FastClick's event listeners.
   *
   * @returns {void}
   */
  FastClick.prototype.destroy = function() {
    var layer = this.layer;

    if (deviceIsAndroid) {
      layer.removeEventListener('mouseover', this.onMouse, true);
      layer.removeEventListener('mousedown', this.onMouse, true);
      layer.removeEventListener('mouseup', this.onMouse, true);
    }

    layer.removeEventListener('click', this.onClick, true);
    layer.removeEventListener('touchstart', this.onTouchStart, false);
    layer.removeEventListener('touchmove', this.onTouchMove, false);
    layer.removeEventListener('touchend', this.onTouchEnd, false);
    layer.removeEventListener('touchcancel', this.onTouchCancel, false);
  };


  /**
   * Check whether FastClick is needed.
   *
   * @param {Element} layer The layer to listen on
   */
  FastClick.notNeeded = function(layer) {
    var metaViewport;
    var chromeVersion;
    var blackberryVersion;
    var firefoxVersion;

    // Devices that don't support touch don't need FastClick
    if (typeof window.ontouchstart === 'undefined') {
      return true;
    }

    // Chrome version - zero for other browsers
    chromeVersion = +(/Chrome\/([0-9]+)/.exec(navigator.userAgent) || [,0])[1];

    if (chromeVersion) {

      if (deviceIsAndroid) {
        metaViewport = document.querySelector('meta[name=viewport]');

        if (metaViewport) {
          // Chrome on Android with user-scalable="no" doesn't need FastClick (issue #89)
          if (metaViewport.content.indexOf('user-scalable=no') !== -1) {
            return true;
          }
          // Chrome 32 and above with width=device-width or less don't need FastClick
          if (chromeVersion > 31 && document.documentElement.scrollWidth <= window.outerWidth) {
            return true;
          }
        }

      // Chrome desktop doesn't need FastClick (issue #15)
      } else {
        return true;
      }
    }

    if (deviceIsBlackBerry10) {
      blackberryVersion = navigator.userAgent.match(/Version\/([0-9]*)\.([0-9]*)/);

      // BlackBerry 10.3+ does not require Fastclick library.
      // https://github.com/ftlabs/fastclick/issues/251
      if (blackberryVersion[1] >= 10 && blackberryVersion[2] >= 3) {
        metaViewport = document.querySelector('meta[name=viewport]');

        if (metaViewport) {
          // user-scalable=no eliminates click delay.
          if (metaViewport.content.indexOf('user-scalable=no') !== -1) {
            return true;
          }
          // width=device-width (or less than device-width) eliminates click delay.
          if (document.documentElement.scrollWidth <= window.outerWidth) {
            return true;
          }
        }
      }
    }

    // IE10 with -ms-touch-action: none or manipulation, which disables double-tap-to-zoom (issue #97)
    if (layer.style.msTouchAction === 'none' || layer.style.touchAction === 'manipulation') {
      return true;
    }

    // Firefox version - zero for other browsers
    firefoxVersion = +(/Firefox\/([0-9]+)/.exec(navigator.userAgent) || [,0])[1];

    if (firefoxVersion >= 27) {
      // Firefox 27+ does not have tap delay if the content is not zoomable - https://bugzilla.mozilla.org/show_bug.cgi?id=922896

      metaViewport = document.querySelector('meta[name=viewport]');
      if (metaViewport && (metaViewport.content.indexOf('user-scalable=no') !== -1 || document.documentElement.scrollWidth <= window.outerWidth)) {
        return true;
      }
    }

    // IE11: prefixed -ms-touch-action is no longer supported and it's recomended to use non-prefixed version
    // http://msdn.microsoft.com/en-us/library/windows/apps/Hh767313.aspx
    if (layer.style.touchAction === 'none' || layer.style.touchAction === 'manipulation') {
      return true;
    }

    return false;
  };


  /**
   * Factory method for creating a FastClick object
   *
   * @param {Element} layer The layer to listen on
   * @param {Object} [options={}] The options to override the defaults
   */
  FastClick.attach = function(layer, options) {
    return new FastClick(layer, options);
  };


  if (typeof define === 'function' && typeof define.amd === 'object' && define.amd) {

    // AMD. Register as an anonymous module.
    define(function() {
      return FastClick;
    });
  } else if (typeof module !== 'undefined' && module.exports) {
    module.exports = FastClick.attach;
    module.exports.FastClick = FastClick;
  } else {
    window.FastClick = FastClick;
  }
}());
/* Zepto v1.2.0 - zepto event ajax form ie - zeptojs.com/license */

(function(global, factory) {
  if (typeof define === 'function' && define.amd)
    define(function() { return factory(global) })
  else
    factory(global)
}(this, function(window) {
  var Zepto = (function() {
  var undefined, key, $, classList, emptyArray = [], concat = emptyArray.concat, filter = emptyArray.filter, slice = emptyArray.slice,
    document = window.document,
    elementDisplay = {}, classCache = {},
    cssNumber = { 'column-count': 1, 'columns': 1, 'font-weight': 1, 'line-height': 1,'opacity': 1, 'z-index': 1, 'zoom': 1 },
    fragmentRE = /^\s*<(\w+|!)[^>]*>/,
    singleTagRE = /^<(\w+)\s*\/?>(?:<\/\1>|)$/,
    tagExpanderRE = /<(?!area|br|col|embed|hr|img|input|link|meta|param)(([\w:]+)[^>]*)\/>/ig,
    rootNodeRE = /^(?:body|html)$/i,
    capitalRE = /([A-Z])/g,

    // special attributes that should be get/set via method calls
    methodAttributes = ['val', 'css', 'html', 'text', 'data', 'width', 'height', 'offset'],

    adjacencyOperators = [ 'after', 'prepend', 'before', 'append' ],
    table = document.createElement('table'),
    tableRow = document.createElement('tr'),
    containers = {
      'tr': document.createElement('tbody'),
      'tbody': table, 'thead': table, 'tfoot': table,
      'td': tableRow, 'th': tableRow,
      '*': document.createElement('div')
    },
    readyRE = /complete|loaded|interactive/,
    simpleSelectorRE = /^[\w-]*$/,
    class2type = {},
    toString = class2type.toString,
    zepto = {},
    camelize, uniq,
    tempParent = document.createElement('div'),
    propMap = {
      'tabindex': 'tabIndex',
      'readonly': 'readOnly',
      'for': 'htmlFor',
      'class': 'className',
      'maxlength': 'maxLength',
      'cellspacing': 'cellSpacing',
      'cellpadding': 'cellPadding',
      'rowspan': 'rowSpan',
      'colspan': 'colSpan',
      'usemap': 'useMap',
      'frameborder': 'frameBorder',
      'contenteditable': 'contentEditable'
    },
    isArray = Array.isArray ||
      function(object){ return object instanceof Array }

  zepto.matches = function(element, selector) {
    if (!selector || !element || element.nodeType !== 1) return false
    var matchesSelector = element.matches || element.webkitMatchesSelector ||
                          element.mozMatchesSelector || element.oMatchesSelector ||
                          element.matchesSelector
    if (matchesSelector) return matchesSelector.call(element, selector)
    // fall back to performing a selector:
    var match, parent = element.parentNode, temp = !parent
    if (temp) (parent = tempParent).appendChild(element)
    match = ~zepto.qsa(parent, selector).indexOf(element)
    temp && tempParent.removeChild(element)
    return match
  }

  function type(obj) {
    return obj == null ? String(obj) :
      class2type[toString.call(obj)] || "object"
  }

  function isFunction(value) { return type(value) == "function" }
  function isWindow(obj)     { return obj != null && obj == obj.window }
  function isDocument(obj)   { return obj != null && obj.nodeType == obj.DOCUMENT_NODE }
  function isObject(obj)     { return type(obj) == "object" }
  function isPlainObject(obj) {
    return isObject(obj) && !isWindow(obj) && Object.getPrototypeOf(obj) == Object.prototype
  }

  function likeArray(obj) {
    var length = !!obj && 'length' in obj && obj.length,
      type = $.type(obj)

    return 'function' != type && !isWindow(obj) && (
      'array' == type || length === 0 ||
        (typeof length == 'number' && length > 0 && (length - 1) in obj)
    )
  }

  function compact(array) { return filter.call(array, function(item){ return item != null }) }
  function flatten(array) { return array.length > 0 ? $.fn.concat.apply([], array) : array }
  camelize = function(str){ return str.replace(/-+(.)?/g, function(match, chr){ return chr ? chr.toUpperCase() : '' }) }
  function dasherize(str) {
    return str.replace(/::/g, '/')
           .replace(/([A-Z]+)([A-Z][a-z])/g, '$1_$2')
           .replace(/([a-z\d])([A-Z])/g, '$1_$2')
           .replace(/_/g, '-')
           .toLowerCase()
  }
  uniq = function(array){ return filter.call(array, function(item, idx){ return array.indexOf(item) == idx }) }

  function classRE(name) {
    return name in classCache ?
      classCache[name] : (classCache[name] = new RegExp('(^|\\s)' + name + '(\\s|$)'))
  }

  function maybeAddPx(name, value) {
    return (typeof value == "number" && !cssNumber[dasherize(name)]) ? value + "px" : value
  }

  function defaultDisplay(nodeName) {
    var element, display
    if (!elementDisplay[nodeName]) {
      element = document.createElement(nodeName)
      document.body.appendChild(element)
      display = getComputedStyle(element, '').getPropertyValue("display")
      element.parentNode.removeChild(element)
      display == "none" && (display = "block")
      elementDisplay[nodeName] = display
    }
    return elementDisplay[nodeName]
  }

  function children(element) {
    return 'children' in element ?
      slice.call(element.children) :
      $.map(element.childNodes, function(node){ if (node.nodeType == 1) return node })
  }

  function Z(dom, selector) {
    var i, len = dom ? dom.length : 0
    for (i = 0; i < len; i++) this[i] = dom[i]
    this.length = len
    this.selector = selector || ''
  }

  // `$.zepto.fragment` takes a html string and an optional tag name
  // to generate DOM nodes from the given html string.
  // The generated DOM nodes are returned as an array.
  // This function can be overridden in plugins for example to make
  // it compatible with browsers that don't support the DOM fully.
  zepto.fragment = function(html, name, properties) {
    var dom, nodes, container

    // A special case optimization for a single tag
    if (singleTagRE.test(html)) dom = $(document.createElement(RegExp.$1))

    if (!dom) {
      if (html.replace) html = html.replace(tagExpanderRE, "<$1></$2>")
      if (name === undefined) name = fragmentRE.test(html) && RegExp.$1
      if (!(name in containers)) name = '*'

      container = containers[name]
      container.innerHTML = '' + html
      dom = $.each(slice.call(container.childNodes), function(){
        container.removeChild(this)
      })
    }

    if (isPlainObject(properties)) {
      nodes = $(dom)
      $.each(properties, function(key, value) {
        if (methodAttributes.indexOf(key) > -1) nodes[key](value)
        else nodes.attr(key, value)
      })
    }

    return dom
  }

  // `$.zepto.Z` swaps out the prototype of the given `dom` array
  // of nodes with `$.fn` and thus supplying all the Zepto functions
  // to the array. This method can be overridden in plugins.
  zepto.Z = function(dom, selector) {
    return new Z(dom, selector)
  }

  // `$.zepto.isZ` should return `true` if the given object is a Zepto
  // collection. This method can be overridden in plugins.
  zepto.isZ = function(object) {
    return object instanceof zepto.Z
  }

  // `$.zepto.init` is Zepto's counterpart to jQuery's `$.fn.init` and
  // takes a CSS selector and an optional context (and handles various
  // special cases).
  // This method can be overridden in plugins.
  zepto.init = function(selector, context) {
    var dom
    // If nothing given, return an empty Zepto collection
    if (!selector) return zepto.Z()
    // Optimize for string selectors
    else if (typeof selector == 'string') {
      selector = selector.trim()
      // If it's a html fragment, create nodes from it
      // Note: In both Chrome 21 and Firefox 15, DOM error 12
      // is thrown if the fragment doesn't begin with <
      if (selector[0] == '<' && fragmentRE.test(selector))
        dom = zepto.fragment(selector, RegExp.$1, context), selector = null
      // If there's a context, create a collection on that context first, and select
      // nodes from there
      else if (context !== undefined) return $(context).find(selector)
      // If it's a CSS selector, use it to select nodes.
      else dom = zepto.qsa(document, selector)
    }
    // If a function is given, call it when the DOM is ready
    else if (isFunction(selector)) return $(document).ready(selector)
    // If a Zepto collection is given, just return it
    else if (zepto.isZ(selector)) return selector
    else {
      // normalize array if an array of nodes is given
      if (isArray(selector)) dom = compact(selector)
      // Wrap DOM nodes.
      else if (isObject(selector))
        dom = [selector], selector = null
      // If it's a html fragment, create nodes from it
      else if (fragmentRE.test(selector))
        dom = zepto.fragment(selector.trim(), RegExp.$1, context), selector = null
      // If there's a context, create a collection on that context first, and select
      // nodes from there
      else if (context !== undefined) return $(context).find(selector)
      // And last but no least, if it's a CSS selector, use it to select nodes.
      else dom = zepto.qsa(document, selector)
    }
    // create a new Zepto collection from the nodes found
    return zepto.Z(dom, selector)
  }

  // `$` will be the base `Zepto` object. When calling this
  // function just call `$.zepto.init, which makes the implementation
  // details of selecting nodes and creating Zepto collections
  // patchable in plugins.
  $ = function(selector, context){
    return zepto.init(selector, context)
  }

  function extend(target, source, deep) {
    for (key in source)
      if (deep && (isPlainObject(source[key]) || isArray(source[key]))) {
        if (isPlainObject(source[key]) && !isPlainObject(target[key]))
          target[key] = {}
        if (isArray(source[key]) && !isArray(target[key]))
          target[key] = []
        extend(target[key], source[key], deep)
      }
      else if (source[key] !== undefined) target[key] = source[key]
  }

  // Copy all but undefined properties from one or more
  // objects to the `target` object.
  $.extend = function(target){
    var deep, args = slice.call(arguments, 1)
    if (typeof target == 'boolean') {
      deep = target
      target = args.shift()
    }
    args.forEach(function(arg){ extend(target, arg, deep) })
    return target
  }

  // `$.zepto.qsa` is Zepto's CSS selector implementation which
  // uses `document.querySelectorAll` and optimizes for some special cases, like `#id`.
  // This method can be overridden in plugins.
  zepto.qsa = function(element, selector){
    var found,
        maybeID = selector[0] == '#',
        maybeClass = !maybeID && selector[0] == '.',
        nameOnly = maybeID || maybeClass ? selector.slice(1) : selector, // Ensure that a 1 char tag name still gets checked
        isSimple = simpleSelectorRE.test(nameOnly)
    return (element.getElementById && isSimple && maybeID) ? // Safari DocumentFragment doesn't have getElementById
      ( (found = element.getElementById(nameOnly)) ? [found] : [] ) :
      (element.nodeType !== 1 && element.nodeType !== 9 && element.nodeType !== 11) ? [] :
      slice.call(
        isSimple && !maybeID && element.getElementsByClassName ? // DocumentFragment doesn't have getElementsByClassName/TagName
          maybeClass ? element.getElementsByClassName(nameOnly) : // If it's simple, it could be a class
          element.getElementsByTagName(selector) : // Or a tag
          element.querySelectorAll(selector) // Or it's not simple, and we need to query all
      )
  }

  function filtered(nodes, selector) {
    return selector == null ? $(nodes) : $(nodes).filter(selector)
  }

  $.contains = document.documentElement.contains ?
    function(parent, node) {
      return parent !== node && parent.contains(node)
    } :
    function(parent, node) {
      while (node && (node = node.parentNode))
        if (node === parent) return true
      return false
    }

  function funcArg(context, arg, idx, payload) {
    return isFunction(arg) ? arg.call(context, idx, payload) : arg
  }

  function setAttribute(node, name, value) {
    value == null ? node.removeAttribute(name) : node.setAttribute(name, value)
  }

  // access className property while respecting SVGAnimatedString
  function className(node, value){
    var klass = node.className || '',
        svg   = klass && klass.baseVal !== undefined

    if (value === undefined) return svg ? klass.baseVal : klass
    svg ? (klass.baseVal = value) : (node.className = value)
  }

  // "true"  => true
  // "false" => false
  // "null"  => null
  // "42"    => 42
  // "42.5"  => 42.5
  // "08"    => "08"
  // JSON    => parse if valid
  // String  => self
  function deserializeValue(value) {
    try {
      return value ?
        value == "true" ||
        ( value == "false" ? false :
          value == "null" ? null :
          +value + "" == value ? +value :
          /^[\[\{]/.test(value) ? $.parseJSON(value) :
          value )
        : value
    } catch(e) {
      return value
    }
  }

  $.type = type
  $.isFunction = isFunction
  $.isWindow = isWindow
  $.isArray = isArray
  $.isPlainObject = isPlainObject

  $.isEmptyObject = function(obj) {
    var name
    for (name in obj) return false
    return true
  }

  $.isNumeric = function(val) {
    var num = Number(val), type = typeof val
    return val != null && type != 'boolean' &&
      (type != 'string' || val.length) &&
      !isNaN(num) && isFinite(num) || false
  }

  $.inArray = function(elem, array, i){
    return emptyArray.indexOf.call(array, elem, i)
  }

  $.camelCase = camelize
  $.trim = function(str) {
    return str == null ? "" : String.prototype.trim.call(str)
  }

  // plugin compatibility
  $.uuid = 0
  $.support = { }
  $.expr = { }
  $.noop = function() {}

  $.map = function(elements, callback){
    var value, values = [], i, key
    if (likeArray(elements))
      for (i = 0; i < elements.length; i++) {
        value = callback(elements[i], i)
        if (value != null) values.push(value)
      }
    else
      for (key in elements) {
        value = callback(elements[key], key)
        if (value != null) values.push(value)
      }
    return flatten(values)
  }

  $.each = function(elements, callback){
    var i, key
    if (likeArray(elements)) {
      for (i = 0; i < elements.length; i++)
        if (callback.call(elements[i], i, elements[i]) === false) return elements
    } else {
      for (key in elements)
        if (callback.call(elements[key], key, elements[key]) === false) return elements
    }

    return elements
  }

  $.grep = function(elements, callback){
    return filter.call(elements, callback)
  }

  if (window.JSON) $.parseJSON = JSON.parse

  // Populate the class2type map
  $.each("Boolean Number String Function Array Date RegExp Object Error".split(" "), function(i, name) {
    class2type[ "[object " + name + "]" ] = name.toLowerCase()
  })

  // Define methods that will be available on all
  // Zepto collections
  $.fn = {
    constructor: zepto.Z,
    length: 0,

    // Because a collection acts like an array
    // copy over these useful array functions.
    forEach: emptyArray.forEach,
    reduce: emptyArray.reduce,
    push: emptyArray.push,
    sort: emptyArray.sort,
    splice: emptyArray.splice,
    indexOf: emptyArray.indexOf,
    concat: function(){
      var i, value, args = []
      for (i = 0; i < arguments.length; i++) {
        value = arguments[i]
        args[i] = zepto.isZ(value) ? value.toArray() : value
      }
      return concat.apply(zepto.isZ(this) ? this.toArray() : this, args)
    },

    // `map` and `slice` in the jQuery API work differently
    // from their array counterparts
    map: function(fn){
      return $($.map(this, function(el, i){ return fn.call(el, i, el) }))
    },
    slice: function(){
      return $(slice.apply(this, arguments))
    },

    ready: function(callback){
      // need to check if document.body exists for IE as that browser reports
      // document ready when it hasn't yet created the body element
      if (readyRE.test(document.readyState) && document.body) callback($)
      else document.addEventListener('DOMContentLoaded', function(){ callback($) }, false)
      return this
    },
    get: function(idx){
      return idx === undefined ? slice.call(this) : this[idx >= 0 ? idx : idx + this.length]
    },
    toArray: function(){ return this.get() },
    size: function(){
      return this.length
    },
    remove: function(){
      return this.each(function(){
        if (this.parentNode != null)
          this.parentNode.removeChild(this)
      })
    },
    each: function(callback){
      emptyArray.every.call(this, function(el, idx){
        return callback.call(el, idx, el) !== false
      })
      return this
    },
    filter: function(selector){
      if (isFunction(selector)) return this.not(this.not(selector))
      return $(filter.call(this, function(element){
        return zepto.matches(element, selector)
      }))
    },
    add: function(selector,context){
      return $(uniq(this.concat($(selector,context))))
    },
    is: function(selector){
      return this.length > 0 && zepto.matches(this[0], selector)
    },
    not: function(selector){
      var nodes=[]
      if (isFunction(selector) && selector.call !== undefined)
        this.each(function(idx){
          if (!selector.call(this,idx)) nodes.push(this)
        })
      else {
        var excludes = typeof selector == 'string' ? this.filter(selector) :
          (likeArray(selector) && isFunction(selector.item)) ? slice.call(selector) : $(selector)
        this.forEach(function(el){
          if (excludes.indexOf(el) < 0) nodes.push(el)
        })
      }
      return $(nodes)
    },
    has: function(selector){
      return this.filter(function(){
        return isObject(selector) ?
          $.contains(this, selector) :
          $(this).find(selector).size()
      })
    },
    eq: function(idx){
      return idx === -1 ? this.slice(idx) : this.slice(idx, + idx + 1)
    },
    first: function(){
      var el = this[0]
      return el && !isObject(el) ? el : $(el)
    },
    last: function(){
      var el = this[this.length - 1]
      return el && !isObject(el) ? el : $(el)
    },
    find: function(selector){
      var result, $this = this
      if (!selector) result = $()
      else if (typeof selector == 'object')
        result = $(selector).filter(function(){
          var node = this
          return emptyArray.some.call($this, function(parent){
            return $.contains(parent, node)
          })
        })
      else if (this.length == 1) result = $(zepto.qsa(this[0], selector))
      else result = this.map(function(){ return zepto.qsa(this, selector) })
      return result
    },
    closest: function(selector, context){
      var nodes = [], collection = typeof selector == 'object' && $(selector)
      this.each(function(_, node){
        while (node && !(collection ? collection.indexOf(node) >= 0 : zepto.matches(node, selector)))
          node = node !== context && !isDocument(node) && node.parentNode
        if (node && nodes.indexOf(node) < 0) nodes.push(node)
      })
      return $(nodes)
    },
    parents: function(selector){
      var ancestors = [], nodes = this
      while (nodes.length > 0)
        nodes = $.map(nodes, function(node){
          if ((node = node.parentNode) && !isDocument(node) && ancestors.indexOf(node) < 0) {
            ancestors.push(node)
            return node
          }
        })
      return filtered(ancestors, selector)
    },
    parent: function(selector){
      return filtered(uniq(this.pluck('parentNode')), selector)
    },
    children: function(selector){
      return filtered(this.map(function(){ return children(this) }), selector)
    },
    contents: function() {
      return this.map(function() { return this.contentDocument || slice.call(this.childNodes) })
    },
    siblings: function(selector){
      return filtered(this.map(function(i, el){
        return filter.call(children(el.parentNode), function(child){ return child!==el })
      }), selector)
    },
    empty: function(){
      return this.each(function(){ this.innerHTML = '' })
    },
    // `pluck` is borrowed from Prototype.js
    pluck: function(property){
      return $.map(this, function(el){ return el[property] })
    },
    show: function(){
      return this.each(function(){
        this.style.display == "none" && (this.style.display = '')
        if (getComputedStyle(this, '').getPropertyValue("display") == "none")
          this.style.display = defaultDisplay(this.nodeName)
      })
    },
    replaceWith: function(newContent){
      return this.before(newContent).remove()
    },
    wrap: function(structure){
      var func = isFunction(structure)
      if (this[0] && !func)
        var dom   = $(structure).get(0),
            clone = dom.parentNode || this.length > 1

      return this.each(function(index){
        $(this).wrapAll(
          func ? structure.call(this, index) :
            clone ? dom.cloneNode(true) : dom
        )
      })
    },
    wrapAll: function(structure){
      if (this[0]) {
        $(this[0]).before(structure = $(structure))
        var children
        // drill down to the inmost element
        while ((children = structure.children()).length) structure = children.first()
        $(structure).append(this)
      }
      return this
    },
    wrapInner: function(structure){
      var func = isFunction(structure)
      return this.each(function(index){
        var self = $(this), contents = self.contents(),
            dom  = func ? structure.call(this, index) : structure
        contents.length ? contents.wrapAll(dom) : self.append(dom)
      })
    },
    unwrap: function(){
      this.parent().each(function(){
        $(this).replaceWith($(this).children())
      })
      return this
    },
    clone: function(){
      return this.map(function(){ return this.cloneNode(true) })
    },
    hide: function(){
      return this.css("display", "none")
    },
    toggle: function(setting){
      return this.each(function(){
        var el = $(this)
        ;(setting === undefined ? el.css("display") == "none" : setting) ? el.show() : el.hide()
      })
    },
    prev: function(selector){ return $(this.pluck('previousElementSibling')).filter(selector || '*') },
    next: function(selector){ return $(this.pluck('nextElementSibling')).filter(selector || '*') },
    html: function(html){
      return 0 in arguments ?
        this.each(function(idx){
          var originHtml = this.innerHTML
          $(this).empty().append( funcArg(this, html, idx, originHtml) )
        }) :
        (0 in this ? this[0].innerHTML : null)
    },
    text: function(text){
      return 0 in arguments ?
        this.each(function(idx){
          var newText = funcArg(this, text, idx, this.textContent)
          this.textContent = newText == null ? '' : ''+newText
        }) :
        (0 in this ? this.pluck('textContent').join("") : null)
    },
    attr: function(name, value){
      var result
      return (typeof name == 'string' && !(1 in arguments)) ?
        (0 in this && this[0].nodeType == 1 && (result = this[0].getAttribute(name)) != null ? result : undefined) :
        this.each(function(idx){
          if (this.nodeType !== 1) return
          if (isObject(name)) for (key in name) setAttribute(this, key, name[key])
          else setAttribute(this, name, funcArg(this, value, idx, this.getAttribute(name)))
        })
    },
    removeAttr: function(name){
      return this.each(function(){ this.nodeType === 1 && name.split(' ').forEach(function(attribute){
        setAttribute(this, attribute)
      }, this)})
    },
    prop: function(name, value){
      name = propMap[name] || name
      return (1 in arguments) ?
        this.each(function(idx){
          this[name] = funcArg(this, value, idx, this[name])
        }) :
        (this[0] && this[0][name])
    },
    removeProp: function(name){
      name = propMap[name] || name
      return this.each(function(){ delete this[name] })
    },
    data: function(name, value){
      var attrName = 'data-' + name.replace(capitalRE, '-$1').toLowerCase()

      var data = (1 in arguments) ?
        this.attr(attrName, value) :
        this.attr(attrName)

      return data !== null ? deserializeValue(data) : undefined
    },
    val: function(value){
      if (0 in arguments) {
        if (value == null) value = ""
        return this.each(function(idx){
          this.value = funcArg(this, value, idx, this.value)
        })
      } else {
        return this[0] && (this[0].multiple ?
           $(this[0]).find('option').filter(function(){ return this.selected }).pluck('value') :
           this[0].value)
      }
    },
    offset: function(coordinates){
      if (coordinates) return this.each(function(index){
        var $this = $(this),
            coords = funcArg(this, coordinates, index, $this.offset()),
            parentOffset = $this.offsetParent().offset(),
            props = {
              top:  coords.top  - parentOffset.top,
              left: coords.left - parentOffset.left
            }

        if ($this.css('position') == 'static') props['position'] = 'relative'
        $this.css(props)
      })
      if (!this.length) return null
      if (document.documentElement !== this[0] && !$.contains(document.documentElement, this[0]))
        return {top: 0, left: 0}
      var obj = this[0].getBoundingClientRect()
      return {
        left: obj.left + window.pageXOffset,
        top: obj.top + window.pageYOffset,
        width: Math.round(obj.width),
        height: Math.round(obj.height)
      }
    },
    css: function(property, value){
      if (arguments.length < 2) {
        var element = this[0]
        if (typeof property == 'string') {
          if (!element) return
          return element.style[camelize(property)] || getComputedStyle(element, '').getPropertyValue(property)
        } else if (isArray(property)) {
          if (!element) return
          var props = {}
          var computedStyle = getComputedStyle(element, '')
          $.each(property, function(_, prop){
            props[prop] = (element.style[camelize(prop)] || computedStyle.getPropertyValue(prop))
          })
          return props
        }
      }

      var css = ''
      if (type(property) == 'string') {
        if (!value && value !== 0)
          this.each(function(){ this.style.removeProperty(dasherize(property)) })
        else
          css = dasherize(property) + ":" + maybeAddPx(property, value)
      } else {
        for (key in property)
          if (!property[key] && property[key] !== 0)
            this.each(function(){ this.style.removeProperty(dasherize(key)) })
          else
            css += dasherize(key) + ':' + maybeAddPx(key, property[key]) + ';'
      }

      return this.each(function(){ this.style.cssText += ';' + css })
    },
    index: function(element){
      return element ? this.indexOf($(element)[0]) : this.parent().children().indexOf(this[0])
    },
    hasClass: function(name){
      if (!name) return false
      return emptyArray.some.call(this, function(el){
        return this.test(className(el))
      }, classRE(name))
    },
    addClass: function(name){
      if (!name) return this
      return this.each(function(idx){
        if (!('className' in this)) return
        classList = []
        var cls = className(this), newName = funcArg(this, name, idx, cls)
        newName.split(/\s+/g).forEach(function(klass){
          if (!$(this).hasClass(klass)) classList.push(klass)
        }, this)
        classList.length && className(this, cls + (cls ? " " : "") + classList.join(" "))
      })
    },
    removeClass: function(name){
      return this.each(function(idx){
        if (!('className' in this)) return
        if (name === undefined) return className(this, '')
        classList = className(this)
        funcArg(this, name, idx, classList).split(/\s+/g).forEach(function(klass){
          classList = classList.replace(classRE(klass), " ")
        })
        className(this, classList.trim())
      })
    },
    toggleClass: function(name, when){
      if (!name) return this
      return this.each(function(idx){
        var $this = $(this), names = funcArg(this, name, idx, className(this))
        names.split(/\s+/g).forEach(function(klass){
          (when === undefined ? !$this.hasClass(klass) : when) ?
            $this.addClass(klass) : $this.removeClass(klass)
        })
      })
    },
    scrollTop: function(value){
      if (!this.length) return
      var hasScrollTop = 'scrollTop' in this[0]
      if (value === undefined) return hasScrollTop ? this[0].scrollTop : this[0].pageYOffset
      return this.each(hasScrollTop ?
        function(){ this.scrollTop = value } :
        function(){ this.scrollTo(this.scrollX, value) })
    },
    scrollLeft: function(value){
      if (!this.length) return
      var hasScrollLeft = 'scrollLeft' in this[0]
      if (value === undefined) return hasScrollLeft ? this[0].scrollLeft : this[0].pageXOffset
      return this.each(hasScrollLeft ?
        function(){ this.scrollLeft = value } :
        function(){ this.scrollTo(value, this.scrollY) })
    },
    position: function() {
      if (!this.length) return

      var elem = this[0],
        // Get *real* offsetParent
        offsetParent = this.offsetParent(),
        // Get correct offsets
        offset       = this.offset(),
        parentOffset = rootNodeRE.test(offsetParent[0].nodeName) ? { top: 0, left: 0 } : offsetParent.offset()

      // Subtract element margins
      // note: when an element has margin: auto the offsetLeft and marginLeft
      // are the same in Safari causing offset.left to incorrectly be 0
      offset.top  -= parseFloat( $(elem).css('margin-top') ) || 0
      offset.left -= parseFloat( $(elem).css('margin-left') ) || 0

      // Add offsetParent borders
      parentOffset.top  += parseFloat( $(offsetParent[0]).css('border-top-width') ) || 0
      parentOffset.left += parseFloat( $(offsetParent[0]).css('border-left-width') ) || 0

      // Subtract the two offsets
      return {
        top:  offset.top  - parentOffset.top,
        left: offset.left - parentOffset.left
      }
    },
    offsetParent: function() {
      return this.map(function(){
        var parent = this.offsetParent || document.body
        while (parent && !rootNodeRE.test(parent.nodeName) && $(parent).css("position") == "static")
          parent = parent.offsetParent
        return parent
      })
    }
  }

  // for now
  $.fn.detach = $.fn.remove

  // Generate the `width` and `height` functions
  ;['width', 'height'].forEach(function(dimension){
    var dimensionProperty =
      dimension.replace(/./, function(m){ return m[0].toUpperCase() })

    $.fn[dimension] = function(value){
      var offset, el = this[0]
      if (value === undefined) return isWindow(el) ? el['inner' + dimensionProperty] :
        isDocument(el) ? el.documentElement['scroll' + dimensionProperty] :
        (offset = this.offset()) && offset[dimension]
      else return this.each(function(idx){
        el = $(this)
        el.css(dimension, funcArg(this, value, idx, el[dimension]()))
      })
    }
  })

  function traverseNode(node, fun) {
    fun(node)
    for (var i = 0, len = node.childNodes.length; i < len; i++)
      traverseNode(node.childNodes[i], fun)
  }

  // Generate the `after`, `prepend`, `before`, `append`,
  // `insertAfter`, `insertBefore`, `appendTo`, and `prependTo` methods.
  adjacencyOperators.forEach(function(operator, operatorIndex) {
    var inside = operatorIndex % 2 //=> prepend, append

    $.fn[operator] = function(){
      // arguments can be nodes, arrays of nodes, Zepto objects and HTML strings
      var argType, nodes = $.map(arguments, function(arg) {
            var arr = []
            argType = type(arg)
            if (argType == "array") {
              arg.forEach(function(el) {
                if (el.nodeType !== undefined) return arr.push(el)
                else if ($.zepto.isZ(el)) return arr = arr.concat(el.get())
                arr = arr.concat(zepto.fragment(el))
              })
              return arr
            }
            return argType == "object" || arg == null ?
              arg : zepto.fragment(arg)
          }),
          parent, copyByClone = this.length > 1
      if (nodes.length < 1) return this

      return this.each(function(_, target){
        parent = inside ? target : target.parentNode

        // convert all methods to a "before" operation
        target = operatorIndex == 0 ? target.nextSibling :
                 operatorIndex == 1 ? target.firstChild :
                 operatorIndex == 2 ? target :
                 null

        var parentInDocument = $.contains(document.documentElement, parent)

        nodes.forEach(function(node){
          if (copyByClone) node = node.cloneNode(true)
          else if (!parent) return $(node).remove()

          parent.insertBefore(node, target)
          if (parentInDocument) traverseNode(node, function(el){
            if (el.nodeName != null && el.nodeName.toUpperCase() === 'SCRIPT' &&
               (!el.type || el.type === 'text/javascript') && !el.src){
              var target = el.ownerDocument ? el.ownerDocument.defaultView : window
              target['eval'].call(target, el.innerHTML)
            }
          })
        })
      })
    }

    // after    => insertAfter
    // prepend  => prependTo
    // before   => insertBefore
    // append   => appendTo
    $.fn[inside ? operator+'To' : 'insert'+(operatorIndex ? 'Before' : 'After')] = function(html){
      $(html)[operator](this)
      return this
    }
  })

  zepto.Z.prototype = Z.prototype = $.fn

  // Export internal API functions in the `$.zepto` namespace
  zepto.uniq = uniq
  zepto.deserializeValue = deserializeValue
  $.zepto = zepto

  return $
})()

window.Zepto = Zepto
window.$ === undefined && (window.$ = Zepto)

;(function($){
  var _zid = 1, undefined,
      slice = Array.prototype.slice,
      isFunction = $.isFunction,
      isString = function(obj){ return typeof obj == 'string' },
      handlers = {},
      specialEvents={},
      focusinSupported = 'onfocusin' in window,
      focus = { focus: 'focusin', blur: 'focusout' },
      hover = { mouseenter: 'mouseover', mouseleave: 'mouseout' }

  specialEvents.click = specialEvents.mousedown = specialEvents.mouseup = specialEvents.mousemove = 'MouseEvents'

  function zid(element) {
    return element._zid || (element._zid = _zid++)
  }
  function findHandlers(element, event, fn, selector) {
    event = parse(event)
    if (event.ns) var matcher = matcherFor(event.ns)
    return (handlers[zid(element)] || []).filter(function(handler) {
      return handler
        && (!event.e  || handler.e == event.e)
        && (!event.ns || matcher.test(handler.ns))
        && (!fn       || zid(handler.fn) === zid(fn))
        && (!selector || handler.sel == selector)
    })
  }
  function parse(event) {
    var parts = ('' + event).split('.')
    return {e: parts[0], ns: parts.slice(1).sort().join(' ')}
  }
  function matcherFor(ns) {
    return new RegExp('(?:^| )' + ns.replace(' ', ' .* ?') + '(?: |$)')
  }

  function eventCapture(handler, captureSetting) {
    return handler.del &&
      (!focusinSupported && (handler.e in focus)) ||
      !!captureSetting
  }

  function realEvent(type) {
    return hover[type] || (focusinSupported && focus[type]) || type
  }

  function add(element, events, fn, data, selector, delegator, capture){
    var id = zid(element), set = (handlers[id] || (handlers[id] = []))
    events.split(/\s/).forEach(function(event){
      if (event == 'ready') return $(document).ready(fn)
      var handler   = parse(event)
      handler.fn    = fn
      handler.sel   = selector
      // emulate mouseenter, mouseleave
      if (handler.e in hover) fn = function(e){
        var related = e.relatedTarget
        if (!related || (related !== this && !$.contains(this, related)))
          return handler.fn.apply(this, arguments)
      }
      handler.del   = delegator
      var callback  = delegator || fn
      handler.proxy = function(e){
        e = compatible(e)
        if (e.isImmediatePropagationStopped()) return
        e.data = data
        var result = callback.apply(element, e._args == undefined ? [e] : [e].concat(e._args))
        if (result === false) e.preventDefault(), e.stopPropagation()
        return result
      }
      handler.i = set.length
      set.push(handler)
      if ('addEventListener' in element)
        element.addEventListener(realEvent(handler.e), handler.proxy, eventCapture(handler, capture))
    })
  }
  function remove(element, events, fn, selector, capture){
    var id = zid(element)
    ;(events || '').split(/\s/).forEach(function(event){
      findHandlers(element, event, fn, selector).forEach(function(handler){
        delete handlers[id][handler.i]
      if ('removeEventListener' in element)
        element.removeEventListener(realEvent(handler.e), handler.proxy, eventCapture(handler, capture))
      })
    })
  }

  $.event = { add: add, remove: remove }

  $.proxy = function(fn, context) {
    var args = (2 in arguments) && slice.call(arguments, 2)
    if (isFunction(fn)) {
      var proxyFn = function(){ return fn.apply(context, args ? args.concat(slice.call(arguments)) : arguments) }
      proxyFn._zid = zid(fn)
      return proxyFn
    } else if (isString(context)) {
      if (args) {
        args.unshift(fn[context], fn)
        return $.proxy.apply(null, args)
      } else {
        return $.proxy(fn[context], fn)
      }
    } else {
      throw new TypeError("expected function")
    }
  }

  $.fn.bind = function(event, data, callback){
    return this.on(event, data, callback)
  }
  $.fn.unbind = function(event, callback){
    return this.off(event, callback)
  }
  $.fn.one = function(event, selector, data, callback){
    return this.on(event, selector, data, callback, 1)
  }

  var returnTrue = function(){return true},
      returnFalse = function(){return false},
      ignoreProperties = /^([A-Z]|returnValue$|layer[XY]$|webkitMovement[XY]$)/,
      eventMethods = {
        preventDefault: 'isDefaultPrevented',
        stopImmediatePropagation: 'isImmediatePropagationStopped',
        stopPropagation: 'isPropagationStopped'
      }

  function compatible(event, source) {
    if (source || !event.isDefaultPrevented) {
      source || (source = event)

      $.each(eventMethods, function(name, predicate) {
        var sourceMethod = source[name]
        event[name] = function(){
          this[predicate] = returnTrue
          return sourceMethod && sourceMethod.apply(source, arguments)
        }
        event[predicate] = returnFalse
      })

      event.timeStamp || (event.timeStamp = Date.now())

      if (source.defaultPrevented !== undefined ? source.defaultPrevented :
          'returnValue' in source ? source.returnValue === false :
          source.getPreventDefault && source.getPreventDefault())
        event.isDefaultPrevented = returnTrue
    }
    return event
  }

  function createProxy(event) {
    var key, proxy = { originalEvent: event }
    for (key in event)
      if (!ignoreProperties.test(key) && event[key] !== undefined) proxy[key] = event[key]

    return compatible(proxy, event)
  }

  $.fn.delegate = function(selector, event, callback){
    return this.on(event, selector, callback)
  }
  $.fn.undelegate = function(selector, event, callback){
    return this.off(event, selector, callback)
  }

  $.fn.live = function(event, callback){
    $(document.body).delegate(this.selector, event, callback)
    return this
  }
  $.fn.die = function(event, callback){
    $(document.body).undelegate(this.selector, event, callback)
    return this
  }

  $.fn.on = function(event, selector, data, callback, one){
    var autoRemove, delegator, $this = this
    if (event && !isString(event)) {
      $.each(event, function(type, fn){
        $this.on(type, selector, data, fn, one)
      })
      return $this
    }

    if (!isString(selector) && !isFunction(callback) && callback !== false)
      callback = data, data = selector, selector = undefined
    if (callback === undefined || data === false)
      callback = data, data = undefined

    if (callback === false) callback = returnFalse

    return $this.each(function(_, element){
      if (one) autoRemove = function(e){
        remove(element, e.type, callback)
        return callback.apply(this, arguments)
      }

      if (selector) delegator = function(e){
        var evt, match = $(e.target).closest(selector, element).get(0)
        if (match && match !== element) {
          evt = $.extend(createProxy(e), {currentTarget: match, liveFired: element})
          return (autoRemove || callback).apply(match, [evt].concat(slice.call(arguments, 1)))
        }
      }

      add(element, event, callback, data, selector, delegator || autoRemove)
    })
  }
  $.fn.off = function(event, selector, callback){
    var $this = this
    if (event && !isString(event)) {
      $.each(event, function(type, fn){
        $this.off(type, selector, fn)
      })
      return $this
    }

    if (!isString(selector) && !isFunction(callback) && callback !== false)
      callback = selector, selector = undefined

    if (callback === false) callback = returnFalse

    return $this.each(function(){
      remove(this, event, callback, selector)
    })
  }

  $.fn.trigger = function(event, args){
    event = (isString(event) || $.isPlainObject(event)) ? $.Event(event) : compatible(event)
    event._args = args
    return this.each(function(){
      // handle focus(), blur() by calling them directly
      if (event.type in focus && typeof this[event.type] == "function") this[event.type]()
      // items in the collection might not be DOM elements
      else if ('dispatchEvent' in this) this.dispatchEvent(event)
      else $(this).triggerHandler(event, args)
    })
  }

  // triggers event handlers on current element just as if an event occurred,
  // doesn't trigger an actual event, doesn't bubble
  $.fn.triggerHandler = function(event, args){
    var e, result
    this.each(function(i, element){
      e = createProxy(isString(event) ? $.Event(event) : event)
      e._args = args
      e.target = element
      $.each(findHandlers(element, event.type || event), function(i, handler){
        result = handler.proxy(e)
        if (e.isImmediatePropagationStopped()) return false
      })
    })
    return result
  }

  // shortcut methods for `.bind(event, fn)` for each event type
  ;('focusin focusout focus blur load resize scroll unload click dblclick '+
  'mousedown mouseup mousemove mouseover mouseout mouseenter mouseleave '+
  'change select keydown keypress keyup error').split(' ').forEach(function(event) {
    $.fn[event] = function(callback) {
      return (0 in arguments) ?
        this.bind(event, callback) :
        this.trigger(event)
    }
  })

  $.Event = function(type, props) {
    if (!isString(type)) props = type, type = props.type
    var event = document.createEvent(specialEvents[type] || 'Events'), bubbles = true
    if (props) for (var name in props) (name == 'bubbles') ? (bubbles = !!props[name]) : (event[name] = props[name])
    event.initEvent(type, bubbles, true)
    return compatible(event)
  }

})(Zepto)

;(function($){
  var jsonpID = +new Date(),
      document = window.document,
      key,
      name,
      rscript = /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
      scriptTypeRE = /^(?:text|application)\/javascript/i,
      xmlTypeRE = /^(?:text|application)\/xml/i,
      jsonType = 'application/json',
      htmlType = 'text/html',
      blankRE = /^\s*$/,
      originAnchor = document.createElement('a')

  originAnchor.href = window.location.href

  // trigger a custom event and return false if it was cancelled
  function triggerAndReturn(context, eventName, data) {
    var event = $.Event(eventName)
    $(context).trigger(event, data)
    return !event.isDefaultPrevented()
  }

  // trigger an Ajax "global" event
  function triggerGlobal(settings, context, eventName, data) {
    if (settings.global) return triggerAndReturn(context || document, eventName, data)
  }

  // Number of active Ajax requests
  $.active = 0

  function ajaxStart(settings) {
    if (settings.global && $.active++ === 0) triggerGlobal(settings, null, 'ajaxStart')
  }
  function ajaxStop(settings) {
    if (settings.global && !(--$.active)) triggerGlobal(settings, null, 'ajaxStop')
  }

  // triggers an extra global event "ajaxBeforeSend" that's like "ajaxSend" but cancelable
  function ajaxBeforeSend(xhr, settings) {
    var context = settings.context
    if (settings.beforeSend.call(context, xhr, settings) === false ||
        triggerGlobal(settings, context, 'ajaxBeforeSend', [xhr, settings]) === false)
      return false

    triggerGlobal(settings, context, 'ajaxSend', [xhr, settings])
  }
  function ajaxSuccess(data, xhr, settings, deferred) {
    var context = settings.context, status = 'success'
    settings.success.call(context, data, status, xhr)
    if (deferred) deferred.resolveWith(context, [data, status, xhr])
    triggerGlobal(settings, context, 'ajaxSuccess', [xhr, settings, data])
    ajaxComplete(status, xhr, settings)
  }
  // type: "timeout", "error", "abort", "parsererror"
  function ajaxError(error, type, xhr, settings, deferred) {
    var context = settings.context
    settings.error.call(context, xhr, type, error)
    if (deferred) deferred.rejectWith(context, [xhr, type, error])
    triggerGlobal(settings, context, 'ajaxError', [xhr, settings, error || type])
    ajaxComplete(type, xhr, settings)
  }
  // status: "success", "notmodified", "error", "timeout", "abort", "parsererror"
  function ajaxComplete(status, xhr, settings) {
    var context = settings.context
    settings.complete.call(context, xhr, status)
    triggerGlobal(settings, context, 'ajaxComplete', [xhr, settings])
    ajaxStop(settings)
  }

  function ajaxDataFilter(data, type, settings) {
    if (settings.dataFilter == empty) return data
    var context = settings.context
    return settings.dataFilter.call(context, data, type)
  }

  // Empty function, used as default callback
  function empty() {}

  $.ajaxJSONP = function(options, deferred){
    if (!('type' in options)) return $.ajax(options)

    var _callbackName = options.jsonpCallback,
      callbackName = ($.isFunction(_callbackName) ?
        _callbackName() : _callbackName) || ('Zepto' + (jsonpID++)),
      script = document.createElement('script'),
      originalCallback = window[callbackName],
      responseData,
      abort = function(errorType) {
        $(script).triggerHandler('error', errorType || 'abort')
      },
      xhr = { abort: abort }, abortTimeout

    if (deferred) deferred.promise(xhr)

    $(script).on('load error', function(e, errorType){
      clearTimeout(abortTimeout)
      $(script).off().remove()

      if (e.type == 'error' || !responseData) {
        ajaxError(null, errorType || 'error', xhr, options, deferred)
      } else {
        ajaxSuccess(responseData[0], xhr, options, deferred)
      }

      window[callbackName] = originalCallback
      if (responseData && $.isFunction(originalCallback))
        originalCallback(responseData[0])

      originalCallback = responseData = undefined
    })

    if (ajaxBeforeSend(xhr, options) === false) {
      abort('abort')
      return xhr
    }

    window[callbackName] = function(){
      responseData = arguments
    }

    script.src = options.url.replace(/\?(.+)=\?/, '?$1=' + callbackName)
    document.head.appendChild(script)

    if (options.timeout > 0) abortTimeout = setTimeout(function(){
      abort('timeout')
    }, options.timeout)

    return xhr
  }

  $.ajaxSettings = {
    // Default type of request
    type: 'GET',
    // Callback that is executed before request
    beforeSend: empty,
    // Callback that is executed if the request succeeds
    success: empty,
    // Callback that is executed the the server drops error
    error: empty,
    // Callback that is executed on request complete (both: error and success)
    complete: empty,
    // The context for the callbacks
    context: null,
    // Whether to trigger "global" Ajax events
    global: true,
    // Transport
    xhr: function () {
      return new window.XMLHttpRequest()
    },
    // MIME types mapping
    // IIS returns Javascript as "application/x-javascript"
    accepts: {
      script: 'text/javascript, application/javascript, application/x-javascript',
      json:   jsonType,
      xml:    'application/xml, text/xml',
      html:   htmlType,
      text:   'text/plain'
    },
    // Whether the request is to another domain
    crossDomain: false,
    // Default timeout
    timeout: 0,
    // Whether data should be serialized to string
    processData: true,
    // Whether the browser should be allowed to cache GET responses
    cache: true,
    //Used to handle the raw response data of XMLHttpRequest.
    //This is a pre-filtering function to sanitize the response.
    //The sanitized response should be returned
    dataFilter: empty
  }

  function mimeToDataType(mime) {
    if (mime) mime = mime.split(';', 2)[0]
    return mime && ( mime == htmlType ? 'html' :
      mime == jsonType ? 'json' :
      scriptTypeRE.test(mime) ? 'script' :
      xmlTypeRE.test(mime) && 'xml' ) || 'text'
  }

  function appendQuery(url, query) {
    if (query == '') return url
    return (url + '&' + query).replace(/[&?]{1,2}/, '?')
  }

  // serialize payload and append it to the URL for GET requests
  function serializeData(options) {
    if (options.processData && options.data && $.type(options.data) != "string")
      options.data = $.param(options.data, options.traditional)
    if (options.data && (!options.type || options.type.toUpperCase() == 'GET' || 'jsonp' == options.dataType))
      options.url = appendQuery(options.url, options.data), options.data = undefined
  }

  $.ajax = function(options){
    var settings = $.extend({}, options || {}),
        deferred = $.Deferred && $.Deferred(),
        urlAnchor, hashIndex
    for (key in $.ajaxSettings) if (settings[key] === undefined) settings[key] = $.ajaxSettings[key]

    ajaxStart(settings)

    if (!settings.crossDomain) {
      urlAnchor = document.createElement('a')
      urlAnchor.href = settings.url
      // cleans up URL for .href (IE only), see https://github.com/madrobby/zepto/pull/1049
      urlAnchor.href = urlAnchor.href
      settings.crossDomain = (originAnchor.protocol + '//' + originAnchor.host) !== (urlAnchor.protocol + '//' + urlAnchor.host)
    }

    if (!settings.url) settings.url = window.location.toString()
    if ((hashIndex = settings.url.indexOf('#')) > -1) settings.url = settings.url.slice(0, hashIndex)
    serializeData(settings)

    var dataType = settings.dataType, hasPlaceholder = /\?.+=\?/.test(settings.url)
    if (hasPlaceholder) dataType = 'jsonp'

    if (settings.cache === false || (
         (!options || options.cache !== true) &&
         ('script' == dataType || 'jsonp' == dataType)
        ))
      settings.url = appendQuery(settings.url, '_=' + Date.now())

    if ('jsonp' == dataType) {
      if (!hasPlaceholder)
        settings.url = appendQuery(settings.url,
          settings.jsonp ? (settings.jsonp + '=?') : settings.jsonp === false ? '' : 'callback=?')
      return $.ajaxJSONP(settings, deferred)
    }

    var mime = settings.accepts[dataType],
        headers = { },
        setHeader = function(name, value) { headers[name.toLowerCase()] = [name, value] },
        protocol = /^([\w-]+:)\/\//.test(settings.url) ? RegExp.$1 : window.location.protocol,
        xhr = settings.xhr(),
        nativeSetHeader = xhr.setRequestHeader,
        abortTimeout

    if (deferred) deferred.promise(xhr)

    if (!settings.crossDomain) setHeader('X-Requested-With', 'XMLHttpRequest')
    setHeader('Accept', mime || '*/*')
    if (mime = settings.mimeType || mime) {
      if (mime.indexOf(',') > -1) mime = mime.split(',', 2)[0]
      xhr.overrideMimeType && xhr.overrideMimeType(mime)
    }
    if (settings.contentType || (settings.contentType !== false && settings.data && settings.type.toUpperCase() != 'GET'))
      setHeader('Content-Type', settings.contentType || 'application/x-www-form-urlencoded')

    if (settings.headers) for (name in settings.headers) setHeader(name, settings.headers[name])
    xhr.setRequestHeader = setHeader

    xhr.onreadystatechange = function(){
      if (xhr.readyState == 4) {
        xhr.onreadystatechange = empty
        clearTimeout(abortTimeout)
        var result, error = false
        if ((xhr.status >= 200 && xhr.status < 300) || xhr.status == 304 || (xhr.status == 0 && protocol == 'file:')) {
          dataType = dataType || mimeToDataType(settings.mimeType || xhr.getResponseHeader('content-type'))

          if (xhr.responseType == 'arraybuffer' || xhr.responseType == 'blob')
            result = xhr.response
          else {
            result = xhr.responseText

            try {
              // http://perfectionkills.com/global-eval-what-are-the-options/
              // sanitize response accordingly if data filter callback provided
              result = ajaxDataFilter(result, dataType, settings)
              if (dataType == 'script')    (1,eval)(result)
              else if (dataType == 'xml')  result = xhr.responseXML
              else if (dataType == 'json') result = blankRE.test(result) ? null : $.parseJSON(result)
            } catch (e) { error = e }

            if (error) return ajaxError(error, 'parsererror', xhr, settings, deferred)
          }

          ajaxSuccess(result, xhr, settings, deferred)
        } else {
          ajaxError(xhr.statusText || null, xhr.status ? 'error' : 'abort', xhr, settings, deferred)
        }
      }
    }

    if (ajaxBeforeSend(xhr, settings) === false) {
      xhr.abort()
      ajaxError(null, 'abort', xhr, settings, deferred)
      return xhr
    }

    var async = 'async' in settings ? settings.async : true
    xhr.open(settings.type, settings.url, async, settings.username, settings.password)

    if (settings.xhrFields) for (name in settings.xhrFields) xhr[name] = settings.xhrFields[name]

    for (name in headers) nativeSetHeader.apply(xhr, headers[name])

    if (settings.timeout > 0) abortTimeout = setTimeout(function(){
        xhr.onreadystatechange = empty
        xhr.abort()
        ajaxError(null, 'timeout', xhr, settings, deferred)
      }, settings.timeout)

    // avoid sending empty string (#319)
    xhr.send(settings.data ? settings.data : null)
    return xhr
  }

  // handle optional data/success arguments
  function parseArguments(url, data, success, dataType) {
    if ($.isFunction(data)) dataType = success, success = data, data = undefined
    if (!$.isFunction(success)) dataType = success, success = undefined
    return {
      url: url
    , data: data
    , success: success
    , dataType: dataType
    }
  }

  $.get = function(/* url, data, success, dataType */){
    return $.ajax(parseArguments.apply(null, arguments))
  }

  $.post = function(/* url, data, success, dataType */){
    var options = parseArguments.apply(null, arguments)
    options.type = 'POST'
    return $.ajax(options)
  }

  $.getJSON = function(/* url, data, success */){
    var options = parseArguments.apply(null, arguments)
    options.dataType = 'json'
    return $.ajax(options)
  }

  $.fn.load = function(url, data, success){
    if (!this.length) return this
    var self = this, parts = url.split(/\s/), selector,
        options = parseArguments(url, data, success),
        callback = options.success
    if (parts.length > 1) options.url = parts[0], selector = parts[1]
    options.success = function(response){
      self.html(selector ?
        $('<div>').html(response.replace(rscript, "")).find(selector)
        : response)
      callback && callback.apply(self, arguments)
    }
    $.ajax(options)
    return this
  }

  var escape = encodeURIComponent

  function serialize(params, obj, traditional, scope){
    var type, array = $.isArray(obj), hash = $.isPlainObject(obj)
    $.each(obj, function(key, value) {
      type = $.type(value)
      if (scope) key = traditional ? scope :
        scope + '[' + (hash || type == 'object' || type == 'array' ? key : '') + ']'
      // handle data in serializeArray() format
      if (!scope && array) params.add(value.name, value.value)
      // recurse into nested objects
      else if (type == "array" || (!traditional && type == "object"))
        serialize(params, value, traditional, key)
      else params.add(key, value)
    })
  }

  $.param = function(obj, traditional){
    var params = []
    params.add = function(key, value) {
      if ($.isFunction(value)) value = value()
      if (value == null) value = ""
      this.push(escape(key) + '=' + escape(value))
    }
    serialize(params, obj, traditional)
    return params.join('&').replace(/%20/g, '+')
  }
})(Zepto)

;(function($){
  $.fn.serializeArray = function() {
    var name, type, result = [],
      add = function(value) {
        if (value.forEach) return value.forEach(add)
        result.push({ name: name, value: value })
      }
    if (this[0]) $.each(this[0].elements, function(_, field){
      type = field.type, name = field.name
      if (name && field.nodeName.toLowerCase() != 'fieldset' &&
        !field.disabled && type != 'submit' && type != 'reset' && type != 'button' && type != 'file' &&
        ((type != 'radio' && type != 'checkbox') || field.checked))
          add($(field).val())
    })
    return result
  }

  $.fn.serialize = function(){
    var result = []
    this.serializeArray().forEach(function(elm){
      result.push(encodeURIComponent(elm.name) + '=' + encodeURIComponent(elm.value))
    })
    return result.join('&')
  }

  $.fn.submit = function(callback) {
    if (0 in arguments) this.bind('submit', callback)
    else if (this.length) {
      var event = $.Event('submit')
      this.eq(0).trigger(event)
      if (!event.isDefaultPrevented()) this.get(0).submit()
    }
    return this
  }

})(Zepto)

;(function(){
  // getComputedStyle shouldn't freak out when called
  // without a valid element as argument
  try {
    getComputedStyle(undefined)
  } catch(e) {
    var nativeGetComputedStyle = getComputedStyle
    window.getComputedStyle = function(element, pseudoElement){
      try {
        return nativeGetComputedStyle(element, pseudoElement)
      } catch(e) {
        return null
      }
    }
  }
})()
  return Zepto
}))
;
//     Zepto.js
//     (c) 2010-2016 Thomas Fuchs
//     Zepto.js may be freely distributed under the MIT license.

// The following code is heavily inspired by jQuery's $.fn.data()

;(function($){
  var data = {}, dataAttr = $.fn.data, camelize = $.camelCase,
    exp = $.expando = 'Zepto' + (+new Date()), emptyArray = []

  // Get value from node:
  // 1. first try key as given,
  // 2. then try camelized key,
  // 3. fall back to reading "data-*" attribute.
  function getData(node, name) {
    var id = node[exp], store = id && data[id]
    if (name === undefined) return store || setData(node)
    else {
      if (store) {
        if (name in store) return store[name]
        var camelName = camelize(name)
        if (camelName in store) return store[camelName]
      }
      return dataAttr.call($(node), name)
    }
  }

  // Store value under camelized key on node
  function setData(node, name, value) {
    var id = node[exp] || (node[exp] = ++$.uuid),
      store = data[id] || (data[id] = attributeData(node))
    if (name !== undefined) store[camelize(name)] = value
    return store
  }

  // Read all "data-*" attributes from a node
  function attributeData(node) {
    var store = {}
    $.each(node.attributes || emptyArray, function(i, attr){
      if (attr.name.indexOf('data-') == 0)
        store[camelize(attr.name.replace('data-', ''))] =
          $.zepto.deserializeValue(attr.value)
    })
    return store
  }

  $.fn.data = function(name, value) {
    return value === undefined ?
      // set multiple values via object
      $.isPlainObject(name) ?
        this.each(function(i, node){
          $.each(name, function(key, value){ setData(node, key, value) })
        }) :
        // get value from first element
        (0 in this ? getData(this[0], name) : undefined) :
      // set value on all elements
      this.each(function(){ setData(this, name, value) })
  }

  $.data = function(elem, name, value) {
    return $(elem).data(name, value)
  }

  $.hasData = function(elem) {
    var id = elem[exp], store = id && data[id]
    return store ? !$.isEmptyObject(store) : false
  }

  $.fn.removeData = function(names) {
    if (typeof names == 'string') names = names.split(/\s+/)
    return this.each(function(){
      var id = this[exp], store = id && data[id]
      if (store) $.each(names || store, function(key){
        delete store[names ? camelize(this) : key]
      })
    })
  }

  // Generate extended `remove` and `empty` functions
  ;['remove', 'empty'].forEach(function(methodName){
    var origFn = $.fn[methodName]
    $.fn[methodName] = function() {
      var elements = this.find('*')
      if (methodName === 'remove') elements = elements.add(this)
      elements.removeData()
      return origFn.call(this)
    }
  })
})(Zepto)
;
//     Zepto.js
//     (c) 2010-2016 Thomas Fuchs
//     Zepto.js may be freely distributed under the MIT license.

;(function($, undefined){
  var prefix = '', eventPrefix,
    vendors = { Webkit: 'webkit', Moz: '', O: 'o' },
    testEl = document.createElement('div'),
    supportedTransforms = /^((translate|rotate|scale)(X|Y|Z|3d)?|matrix(3d)?|perspective|skew(X|Y)?)$/i,
    transform,
    transitionProperty, transitionDuration, transitionTiming, transitionDelay,
    animationName, animationDuration, animationTiming, animationDelay,
    cssReset = {}

  function dasherize(str) { return str.replace(/([A-Z])/g, '-$1').toLowerCase() }
  function normalizeEvent(name) { return eventPrefix ? eventPrefix + name : name.toLowerCase() }

  if (testEl.style.transform === undefined) $.each(vendors, function(vendor, event){
    if (testEl.style[vendor + 'TransitionProperty'] !== undefined) {
      prefix = '-' + vendor.toLowerCase() + '-'
      eventPrefix = event
      return false
    }
  })

  transform = prefix + 'transform'
  cssReset[transitionProperty = prefix + 'transition-property'] =
  cssReset[transitionDuration = prefix + 'transition-duration'] =
  cssReset[transitionDelay    = prefix + 'transition-delay'] =
  cssReset[transitionTiming   = prefix + 'transition-timing-function'] =
  cssReset[animationName      = prefix + 'animation-name'] =
  cssReset[animationDuration  = prefix + 'animation-duration'] =
  cssReset[animationDelay     = prefix + 'animation-delay'] =
  cssReset[animationTiming    = prefix + 'animation-timing-function'] = ''

  $.fx = {
    off: (eventPrefix === undefined && testEl.style.transitionProperty === undefined),
    speeds: { _default: 400, fast: 200, slow: 600 },
    cssPrefix: prefix,
    transitionEnd: normalizeEvent('TransitionEnd'),
    animationEnd: normalizeEvent('AnimationEnd')
  }

  $.fn.animate = function(properties, duration, ease, callback, delay){
    if ($.isFunction(duration))
      callback = duration, ease = undefined, duration = undefined
    if ($.isFunction(ease))
      callback = ease, ease = undefined
    if ($.isPlainObject(duration))
      ease = duration.easing, callback = duration.complete, delay = duration.delay, duration = duration.duration
    if (duration) duration = (typeof duration == 'number' ? duration :
                    ($.fx.speeds[duration] || $.fx.speeds._default)) / 1000
    if (delay) delay = parseFloat(delay) / 1000
    return this.anim(properties, duration, ease, callback, delay)
  }

  $.fn.anim = function(properties, duration, ease, callback, delay){
    var key, cssValues = {}, cssProperties, transforms = '',
        that = this, wrappedCallback, endEvent = $.fx.transitionEnd,
        fired = false

    if (duration === undefined) duration = $.fx.speeds._default / 1000
    if (delay === undefined) delay = 0
    if ($.fx.off) duration = 0

    if (typeof properties == 'string') {
      // keyframe animation
      cssValues[animationName] = properties
      cssValues[animationDuration] = duration + 's'
      cssValues[animationDelay] = delay + 's'
      cssValues[animationTiming] = (ease || 'linear')
      endEvent = $.fx.animationEnd
    } else {
      cssProperties = []
      // CSS transitions
      for (key in properties)
        if (supportedTransforms.test(key)) transforms += key + '(' + properties[key] + ') '
        else cssValues[key] = properties[key], cssProperties.push(dasherize(key))

      if (transforms) cssValues[transform] = transforms, cssProperties.push(transform)
      if (duration > 0 && typeof properties === 'object') {
        cssValues[transitionProperty] = cssProperties.join(', ')
        cssValues[transitionDuration] = duration + 's'
        cssValues[transitionDelay] = delay + 's'
        cssValues[transitionTiming] = (ease || 'linear')
      }
    }

    wrappedCallback = function(event){
      if (typeof event !== 'undefined') {
        if (event.target !== event.currentTarget) return // makes sure the event didn't bubble from "below"
        $(event.target).unbind(endEvent, wrappedCallback)
      } else
        $(this).unbind(endEvent, wrappedCallback) // triggered by setTimeout

      fired = true
      $(this).css(cssReset)
      callback && callback.call(this)
    }
    if (duration > 0){
      this.bind(endEvent, wrappedCallback)
      // transitionEnd is not always firing on older Android phones
      // so make sure it gets fired
      setTimeout(function(){
        if (fired) return
        wrappedCallback.call(that)
      }, ((duration + delay) * 1000) + 25)
    }

    // trigger page reflow so new elements can animate
    this.size() && this.get(0).clientLeft

    this.css(cssValues)

    if (duration <= 0) setTimeout(function() {
      that.each(function(){ wrappedCallback.call(this) })
    }, 0)

    return this
  }

  testEl = null
})(Zepto)
;
//     Zepto.js
//     (c) 2010-2016 Thomas Fuchs
//     Zepto.js may be freely distributed under the MIT license.

;(function($){
  var zepto = $.zepto, oldQsa = zepto.qsa, oldMatches = zepto.matches

  function visible(elem){
    elem = $(elem)
    return !!(elem.width() || elem.height()) && elem.css("display") !== "none"
  }

  // Implements a subset from:
  // http://api.jquery.com/category/selectors/jquery-selector-extensions/
  //
  // Each filter function receives the current index, all nodes in the
  // considered set, and a value if there were parentheses. The value
  // of `this` is the node currently being considered. The function returns the
  // resulting node(s), null, or undefined.
  //
  // Complex selectors are not supported:
  //   li:has(label:contains("foo")) + li:has(label:contains("bar"))
  //   ul.inner:first > li
  var filters = $.expr[':'] = {
    visible:  function(){ if (visible(this)) return this },
    hidden:   function(){ if (!visible(this)) return this },
    selected: function(){ if (this.selected) return this },
    checked:  function(){ if (this.checked) return this },
    parent:   function(){ return this.parentNode },
    first:    function(idx){ if (idx === 0) return this },
    last:     function(idx, nodes){ if (idx === nodes.length - 1) return this },
    eq:       function(idx, _, value){ if (idx === value) return this },
    contains: function(idx, _, text){ if ($(this).text().indexOf(text) > -1) return this },
    has:      function(idx, _, sel){ if (zepto.qsa(this, sel).length) return this }
  }

  var filterRe = new RegExp('(.*):(\\w+)(?:\\(([^)]+)\\))?$\\s*'),
      childRe  = /^\s*>/,
      classTag = 'Zepto' + (+new Date())

  function process(sel, fn) {
    // quote the hash in `a[href^=#]` expression
    sel = sel.replace(/=#\]/g, '="#"]')
    var filter, arg, match = filterRe.exec(sel)
    if (match && match[2] in filters) {
      filter = filters[match[2]], arg = match[3]
      sel = match[1]
      if (arg) {
        var num = Number(arg)
        if (isNaN(num)) arg = arg.replace(/^["']|["']$/g, '')
        else arg = num
      }
    }
    return fn(sel, filter, arg)
  }

  zepto.qsa = function(node, selector) {
    return process(selector, function(sel, filter, arg){
      try {
        var taggedParent
        if (!sel && filter) sel = '*'
        else if (childRe.test(sel))
          // support "> *" child queries by tagging the parent node with a
          // unique class and prepending that classname onto the selector
          taggedParent = $(node).addClass(classTag), sel = '.'+classTag+' '+sel

        var nodes = oldQsa(node, sel)
      } catch(e) {
        console.error('error performing selector: %o', selector)
        throw e
      } finally {
        if (taggedParent) taggedParent.removeClass(classTag)
      }
      return !filter ? nodes :
        zepto.uniq($.map(nodes, function(n, i){ return filter.call(n, i, nodes, arg) }))
    })
  }

  zepto.matches = function(node, selector){
    return process(selector, function(sel, filter, arg){
      return (!sel || oldMatches(node, sel)) &&
        (!filter || filter.call(node, null, arg) === node)
    })
  }
})(Zepto)
;
/* Author:
    Max Degterev @suprMax
*/


;(function($) {
  var interpolate = function (source, target, shift) {
    return (source + (target - source) * shift);
  };

  var easing = function (pos) {
    return (-Math.cos(pos * Math.PI) / 2) + .5;
  };

  var scroll = function(endY, duration, callback) {
    endY = (typeof endY !== 'undefined') ? endY : ($.os.android ? 1 : 0);
    duration = (typeof duration !== 'undefined') ? duration : 200;

    if (duration === 0) {
      window.scrollTo(0, endY);
      if (typeof callback === 'function') callback();
      return;
    }

    var startY = window.pageYOffset,
        startT = Date.now(),
        finishT = startT + duration;

    var animate = function() {
      var now = Date.now(),
          shift = (now > finishT) ? 1 : (now - startT) / duration;

      window.scrollTo(0, interpolate(startY, endY, easing(shift)));

      if (now < finishT) {
        setTimeout(animate, 15);
      }
      else {
        if (typeof callback === 'function') callback();
      }
    };
  
    animate();
  };

  var scrollNode = function(endY, duration, callback) {
    endY = (typeof endY !== 'undefined') ? endY : 0;
    duration = (typeof duration !== 'undefined') ? duration : 200;

    if (duration === 0) {
      this.scrollTop = endY;
      if (typeof callback === 'function') callback();
      return;
    }

    var startY = this.scrollTop,
        startT = Date.now(),
        finishT = startT + duration,
        _this = this;

    var animate = function() {
      var now = Date.now(),
          shift = (now > finishT) ? 1 : (now - startT) / duration;

      _this.scrollTop = interpolate(startY, endY, easing(shift));

      if (now < finishT) {
        setTimeout(animate, 15);
      }
      else {
        if (typeof callback === 'function') callback();
      }
    };
  
    animate();
  };

  $.scrollTo = scroll;

  $.fn.scrollTo = function() {
    if (this.length) {
      var args = arguments;
      this.forEach(function(elem, index) {
        scrollNode.apply(elem, args);
      });
    }
  };
}(Zepto));
//     Underscore.js 1.5.2
//     http://underscorejs.org
//     (c) 2009-2013 Jeremy Ashkenas, DocumentCloud and Investigative Reporters & Editors
//     Underscore may be freely distributed under the MIT license.
(function(){var n=this,t=n._,r={},e=Array.prototype,u=Object.prototype,i=Function.prototype,a=e.push,o=e.slice,c=e.concat,l=u.toString,f=u.hasOwnProperty,s=e.forEach,p=e.map,h=e.reduce,v=e.reduceRight,g=e.filter,d=e.every,m=e.some,y=e.indexOf,b=e.lastIndexOf,x=Array.isArray,w=Object.keys,_=i.bind,j=function(n){return n instanceof j?n:this instanceof j?(this._wrapped=n,void 0):new j(n)};"undefined"!=typeof exports?("undefined"!=typeof module&&module.exports&&(exports=module.exports=j),exports._=j):n._=j,j.VERSION="1.5.2";var A=j.each=j.forEach=function(n,t,e){if(null!=n)if(s&&n.forEach===s)n.forEach(t,e);else if(n.length===+n.length){for(var u=0,i=n.length;i>u;u++)if(t.call(e,n[u],u,n)===r)return}else for(var a=j.keys(n),u=0,i=a.length;i>u;u++)if(t.call(e,n[a[u]],a[u],n)===r)return};j.map=j.collect=function(n,t,r){var e=[];return null==n?e:p&&n.map===p?n.map(t,r):(A(n,function(n,u,i){e.push(t.call(r,n,u,i))}),e)};var E="Reduce of empty array with no initial value";j.reduce=j.foldl=j.inject=function(n,t,r,e){var u=arguments.length>2;if(null==n&&(n=[]),h&&n.reduce===h)return e&&(t=j.bind(t,e)),u?n.reduce(t,r):n.reduce(t);if(A(n,function(n,i,a){u?r=t.call(e,r,n,i,a):(r=n,u=!0)}),!u)throw new TypeError(E);return r},j.reduceRight=j.foldr=function(n,t,r,e){var u=arguments.length>2;if(null==n&&(n=[]),v&&n.reduceRight===v)return e&&(t=j.bind(t,e)),u?n.reduceRight(t,r):n.reduceRight(t);var i=n.length;if(i!==+i){var a=j.keys(n);i=a.length}if(A(n,function(o,c,l){c=a?a[--i]:--i,u?r=t.call(e,r,n[c],c,l):(r=n[c],u=!0)}),!u)throw new TypeError(E);return r},j.find=j.detect=function(n,t,r){var e;return O(n,function(n,u,i){return t.call(r,n,u,i)?(e=n,!0):void 0}),e},j.filter=j.select=function(n,t,r){var e=[];return null==n?e:g&&n.filter===g?n.filter(t,r):(A(n,function(n,u,i){t.call(r,n,u,i)&&e.push(n)}),e)},j.reject=function(n,t,r){return j.filter(n,function(n,e,u){return!t.call(r,n,e,u)},r)},j.every=j.all=function(n,t,e){t||(t=j.identity);var u=!0;return null==n?u:d&&n.every===d?n.every(t,e):(A(n,function(n,i,a){return(u=u&&t.call(e,n,i,a))?void 0:r}),!!u)};var O=j.some=j.any=function(n,t,e){t||(t=j.identity);var u=!1;return null==n?u:m&&n.some===m?n.some(t,e):(A(n,function(n,i,a){return u||(u=t.call(e,n,i,a))?r:void 0}),!!u)};j.contains=j.include=function(n,t){return null==n?!1:y&&n.indexOf===y?n.indexOf(t)!=-1:O(n,function(n){return n===t})},j.invoke=function(n,t){var r=o.call(arguments,2),e=j.isFunction(t);return j.map(n,function(n){return(e?t:n[t]).apply(n,r)})},j.pluck=function(n,t){return j.map(n,function(n){return n[t]})},j.where=function(n,t,r){return j.isEmpty(t)?r?void 0:[]:j[r?"find":"filter"](n,function(n){for(var r in t)if(t[r]!==n[r])return!1;return!0})},j.findWhere=function(n,t){return j.where(n,t,!0)},j.max=function(n,t,r){if(!t&&j.isArray(n)&&n[0]===+n[0]&&n.length<65535)return Math.max.apply(Math,n);if(!t&&j.isEmpty(n))return-1/0;var e={computed:-1/0,value:-1/0};return A(n,function(n,u,i){var a=t?t.call(r,n,u,i):n;a>e.computed&&(e={value:n,computed:a})}),e.value},j.min=function(n,t,r){if(!t&&j.isArray(n)&&n[0]===+n[0]&&n.length<65535)return Math.min.apply(Math,n);if(!t&&j.isEmpty(n))return 1/0;var e={computed:1/0,value:1/0};return A(n,function(n,u,i){var a=t?t.call(r,n,u,i):n;a<e.computed&&(e={value:n,computed:a})}),e.value},j.shuffle=function(n){var t,r=0,e=[];return A(n,function(n){t=j.random(r++),e[r-1]=e[t],e[t]=n}),e},j.sample=function(n,t,r){return arguments.length<2||r?n[j.random(n.length-1)]:j.shuffle(n).slice(0,Math.max(0,t))};var k=function(n){return j.isFunction(n)?n:function(t){return t[n]}};j.sortBy=function(n,t,r){var e=k(t);return j.pluck(j.map(n,function(n,t,u){return{value:n,index:t,criteria:e.call(r,n,t,u)}}).sort(function(n,t){var r=n.criteria,e=t.criteria;if(r!==e){if(r>e||r===void 0)return 1;if(e>r||e===void 0)return-1}return n.index-t.index}),"value")};var F=function(n){return function(t,r,e){var u={},i=null==r?j.identity:k(r);return A(t,function(r,a){var o=i.call(e,r,a,t);n(u,o,r)}),u}};j.groupBy=F(function(n,t,r){(j.has(n,t)?n[t]:n[t]=[]).push(r)}),j.indexBy=F(function(n,t,r){n[t]=r}),j.countBy=F(function(n,t){j.has(n,t)?n[t]++:n[t]=1}),j.sortedIndex=function(n,t,r,e){r=null==r?j.identity:k(r);for(var u=r.call(e,t),i=0,a=n.length;a>i;){var o=i+a>>>1;r.call(e,n[o])<u?i=o+1:a=o}return i},j.toArray=function(n){return n?j.isArray(n)?o.call(n):n.length===+n.length?j.map(n,j.identity):j.values(n):[]},j.size=function(n){return null==n?0:n.length===+n.length?n.length:j.keys(n).length},j.first=j.head=j.take=function(n,t,r){return null==n?void 0:null==t||r?n[0]:o.call(n,0,t)},j.initial=function(n,t,r){return o.call(n,0,n.length-(null==t||r?1:t))},j.last=function(n,t,r){return null==n?void 0:null==t||r?n[n.length-1]:o.call(n,Math.max(n.length-t,0))},j.rest=j.tail=j.drop=function(n,t,r){return o.call(n,null==t||r?1:t)},j.compact=function(n){return j.filter(n,j.identity)};var M=function(n,t,r){return t&&j.every(n,j.isArray)?c.apply(r,n):(A(n,function(n){j.isArray(n)||j.isArguments(n)?t?a.apply(r,n):M(n,t,r):r.push(n)}),r)};j.flatten=function(n,t){return M(n,t,[])},j.without=function(n){return j.difference(n,o.call(arguments,1))},j.uniq=j.unique=function(n,t,r,e){j.isFunction(t)&&(e=r,r=t,t=!1);var u=r?j.map(n,r,e):n,i=[],a=[];return A(u,function(r,e){(t?e&&a[a.length-1]===r:j.contains(a,r))||(a.push(r),i.push(n[e]))}),i},j.union=function(){return j.uniq(j.flatten(arguments,!0))},j.intersection=function(n){var t=o.call(arguments,1);return j.filter(j.uniq(n),function(n){return j.every(t,function(t){return j.indexOf(t,n)>=0})})},j.difference=function(n){var t=c.apply(e,o.call(arguments,1));return j.filter(n,function(n){return!j.contains(t,n)})},j.zip=function(){for(var n=j.max(j.pluck(arguments,"length").concat(0)),t=new Array(n),r=0;n>r;r++)t[r]=j.pluck(arguments,""+r);return t},j.object=function(n,t){if(null==n)return{};for(var r={},e=0,u=n.length;u>e;e++)t?r[n[e]]=t[e]:r[n[e][0]]=n[e][1];return r},j.indexOf=function(n,t,r){if(null==n)return-1;var e=0,u=n.length;if(r){if("number"!=typeof r)return e=j.sortedIndex(n,t),n[e]===t?e:-1;e=0>r?Math.max(0,u+r):r}if(y&&n.indexOf===y)return n.indexOf(t,r);for(;u>e;e++)if(n[e]===t)return e;return-1},j.lastIndexOf=function(n,t,r){if(null==n)return-1;var e=null!=r;if(b&&n.lastIndexOf===b)return e?n.lastIndexOf(t,r):n.lastIndexOf(t);for(var u=e?r:n.length;u--;)if(n[u]===t)return u;return-1},j.range=function(n,t,r){arguments.length<=1&&(t=n||0,n=0),r=arguments[2]||1;for(var e=Math.max(Math.ceil((t-n)/r),0),u=0,i=new Array(e);e>u;)i[u++]=n,n+=r;return i};var R=function(){};j.bind=function(n,t){var r,e;if(_&&n.bind===_)return _.apply(n,o.call(arguments,1));if(!j.isFunction(n))throw new TypeError;return r=o.call(arguments,2),e=function(){if(!(this instanceof e))return n.apply(t,r.concat(o.call(arguments)));R.prototype=n.prototype;var u=new R;R.prototype=null;var i=n.apply(u,r.concat(o.call(arguments)));return Object(i)===i?i:u}},j.partial=function(n){var t=o.call(arguments,1);return function(){return n.apply(this,t.concat(o.call(arguments)))}},j.bindAll=function(n){var t=o.call(arguments,1);if(0===t.length)throw new Error("bindAll must be passed function names");return A(t,function(t){n[t]=j.bind(n[t],n)}),n},j.memoize=function(n,t){var r={};return t||(t=j.identity),function(){var e=t.apply(this,arguments);return j.has(r,e)?r[e]:r[e]=n.apply(this,arguments)}},j.delay=function(n,t){var r=o.call(arguments,2);return setTimeout(function(){return n.apply(null,r)},t)},j.defer=function(n){return j.delay.apply(j,[n,1].concat(o.call(arguments,1)))},j.throttle=function(n,t,r){var e,u,i,a=null,o=0;r||(r={});var c=function(){o=r.leading===!1?0:new Date,a=null,i=n.apply(e,u)};return function(){var l=new Date;o||r.leading!==!1||(o=l);var f=t-(l-o);return e=this,u=arguments,0>=f?(clearTimeout(a),a=null,o=l,i=n.apply(e,u)):a||r.trailing===!1||(a=setTimeout(c,f)),i}},j.debounce=function(n,t,r){var e,u,i,a,o;return function(){i=this,u=arguments,a=new Date;var c=function(){var l=new Date-a;t>l?e=setTimeout(c,t-l):(e=null,r||(o=n.apply(i,u)))},l=r&&!e;return e||(e=setTimeout(c,t)),l&&(o=n.apply(i,u)),o}},j.once=function(n){var t,r=!1;return function(){return r?t:(r=!0,t=n.apply(this,arguments),n=null,t)}},j.wrap=function(n,t){return function(){var r=[n];return a.apply(r,arguments),t.apply(this,r)}},j.compose=function(){var n=arguments;return function(){for(var t=arguments,r=n.length-1;r>=0;r--)t=[n[r].apply(this,t)];return t[0]}},j.after=function(n,t){return function(){return--n<1?t.apply(this,arguments):void 0}},j.keys=w||function(n){if(n!==Object(n))throw new TypeError("Invalid object");var t=[];for(var r in n)j.has(n,r)&&t.push(r);return t},j.values=function(n){for(var t=j.keys(n),r=t.length,e=new Array(r),u=0;r>u;u++)e[u]=n[t[u]];return e},j.pairs=function(n){for(var t=j.keys(n),r=t.length,e=new Array(r),u=0;r>u;u++)e[u]=[t[u],n[t[u]]];return e},j.invert=function(n){for(var t={},r=j.keys(n),e=0,u=r.length;u>e;e++)t[n[r[e]]]=r[e];return t},j.functions=j.methods=function(n){var t=[];for(var r in n)j.isFunction(n[r])&&t.push(r);return t.sort()},j.extend=function(n){return A(o.call(arguments,1),function(t){if(t)for(var r in t)n[r]=t[r]}),n},j.pick=function(n){var t={},r=c.apply(e,o.call(arguments,1));return A(r,function(r){r in n&&(t[r]=n[r])}),t},j.omit=function(n){var t={},r=c.apply(e,o.call(arguments,1));for(var u in n)j.contains(r,u)||(t[u]=n[u]);return t},j.defaults=function(n){return A(o.call(arguments,1),function(t){if(t)for(var r in t)n[r]===void 0&&(n[r]=t[r])}),n},j.clone=function(n){return j.isObject(n)?j.isArray(n)?n.slice():j.extend({},n):n},j.tap=function(n,t){return t(n),n};var S=function(n,t,r,e){if(n===t)return 0!==n||1/n==1/t;if(null==n||null==t)return n===t;n instanceof j&&(n=n._wrapped),t instanceof j&&(t=t._wrapped);var u=l.call(n);if(u!=l.call(t))return!1;switch(u){case"[object String]":return n==String(t);case"[object Number]":return n!=+n?t!=+t:0==n?1/n==1/t:n==+t;case"[object Date]":case"[object Boolean]":return+n==+t;case"[object RegExp]":return n.source==t.source&&n.global==t.global&&n.multiline==t.multiline&&n.ignoreCase==t.ignoreCase}if("object"!=typeof n||"object"!=typeof t)return!1;for(var i=r.length;i--;)if(r[i]==n)return e[i]==t;var a=n.constructor,o=t.constructor;if(a!==o&&!(j.isFunction(a)&&a instanceof a&&j.isFunction(o)&&o instanceof o))return!1;r.push(n),e.push(t);var c=0,f=!0;if("[object Array]"==u){if(c=n.length,f=c==t.length)for(;c--&&(f=S(n[c],t[c],r,e)););}else{for(var s in n)if(j.has(n,s)&&(c++,!(f=j.has(t,s)&&S(n[s],t[s],r,e))))break;if(f){for(s in t)if(j.has(t,s)&&!c--)break;f=!c}}return r.pop(),e.pop(),f};j.isEqual=function(n,t){return S(n,t,[],[])},j.isEmpty=function(n){if(null==n)return!0;if(j.isArray(n)||j.isString(n))return 0===n.length;for(var t in n)if(j.has(n,t))return!1;return!0},j.isElement=function(n){return!(!n||1!==n.nodeType)},j.isArray=x||function(n){return"[object Array]"==l.call(n)},j.isObject=function(n){return n===Object(n)},A(["Arguments","Function","String","Number","Date","RegExp"],function(n){j["is"+n]=function(t){return l.call(t)=="[object "+n+"]"}}),j.isArguments(arguments)||(j.isArguments=function(n){return!(!n||!j.has(n,"callee"))}),"function"!=typeof/./&&(j.isFunction=function(n){return"function"==typeof n}),j.isFinite=function(n){return isFinite(n)&&!isNaN(parseFloat(n))},j.isNaN=function(n){return j.isNumber(n)&&n!=+n},j.isBoolean=function(n){return n===!0||n===!1||"[object Boolean]"==l.call(n)},j.isNull=function(n){return null===n},j.isUndefined=function(n){return n===void 0},j.has=function(n,t){return f.call(n,t)},j.noConflict=function(){return n._=t,this},j.identity=function(n){return n},j.times=function(n,t,r){for(var e=Array(Math.max(0,n)),u=0;n>u;u++)e[u]=t.call(r,u);return e},j.random=function(n,t){return null==t&&(t=n,n=0),n+Math.floor(Math.random()*(t-n+1))};var I={escape:{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#x27;"}};I.unescape=j.invert(I.escape);var T={escape:new RegExp("["+j.keys(I.escape).join("")+"]","g"),unescape:new RegExp("("+j.keys(I.unescape).join("|")+")","g")};j.each(["escape","unescape"],function(n){j[n]=function(t){return null==t?"":(""+t).replace(T[n],function(t){return I[n][t]})}}),j.result=function(n,t){if(null==n)return void 0;var r=n[t];return j.isFunction(r)?r.call(n):r},j.mixin=function(n){A(j.functions(n),function(t){var r=j[t]=n[t];j.prototype[t]=function(){var n=[this._wrapped];return a.apply(n,arguments),z.call(this,r.apply(j,n))}})};var N=0;j.uniqueId=function(n){var t=++N+"";return n?n+t:t},j.templateSettings={evaluate:/<%([\s\S]+?)%>/g,interpolate:/<%=([\s\S]+?)%>/g,escape:/<%-([\s\S]+?)%>/g};var q=/(.)^/,B={"'":"'","\\":"\\","\r":"r","\n":"n","	":"t","\u2028":"u2028","\u2029":"u2029"},D=/\\|'|\r|\n|\t|\u2028|\u2029/g;j.template=function(n,t,r){var e;r=j.defaults({},r,j.templateSettings);var u=new RegExp([(r.escape||q).source,(r.interpolate||q).source,(r.evaluate||q).source].join("|")+"|$","g"),i=0,a="__p+='";n.replace(u,function(t,r,e,u,o){return a+=n.slice(i,o).replace(D,function(n){return"\\"+B[n]}),r&&(a+="'+\n((__t=("+r+"))==null?'':_.escape(__t))+\n'"),e&&(a+="'+\n((__t=("+e+"))==null?'':__t)+\n'"),u&&(a+="';\n"+u+"\n__p+='"),i=o+t.length,t}),a+="';\n",r.variable||(a="with(obj||{}){\n"+a+"}\n"),a="var __t,__p='',__j=Array.prototype.join,"+"print=function(){__p+=__j.call(arguments,'');};\n"+a+"return __p;\n";try{e=new Function(r.variable||"obj","_",a)}catch(o){throw o.source=a,o}if(t)return e(t,j);var c=function(n){return e.call(this,n,j)};return c.source="function("+(r.variable||"obj")+"){\n"+a+"}",c},j.chain=function(n){return j(n).chain()};var z=function(n){return this._chain?j(n).chain():n};j.mixin(j),A(["pop","push","reverse","shift","sort","splice","unshift"],function(n){var t=e[n];j.prototype[n]=function(){var r=this._wrapped;return t.apply(r,arguments),"shift"!=n&&"splice"!=n||0!==r.length||delete r[0],z.call(this,r)}}),A(["concat","join","slice"],function(n){var t=e[n];j.prototype[n]=function(){return z.call(this,t.apply(this._wrapped,arguments))}}),j.extend(j.prototype,{chain:function(){return this._chain=!0,this},value:function(){return this._wrapped}})}).call(this);
// Backbone.js 0.9.1

// (c) 2010-2012 Jeremy Ashkenas, DocumentCloud Inc.
// Backbone may be freely distributed under the MIT license.
// For all details and documentation:
// http://backbonejs.org
(function(){var i=this,r=i.Backbone,s=Array.prototype.slice,t=Array.prototype.splice,g;g="undefined"!==typeof exports?exports:i.Backbone={};g.VERSION="0.9.1";var f=i._;!f&&"undefined"!==typeof require&&(f=require("underscore"));var h=i.jQuery||i.Zepto||i.ender;g.setDomLibrary=function(a){h=a};g.noConflict=function(){i.Backbone=r;return this};g.emulateHTTP=!1;g.emulateJSON=!1;g.Events={on:function(a,b,c){for(var d,a=a.split(/\s+/),e=this._callbacks||(this._callbacks={});d=a.shift();){d=e[d]||(e[d]=
{});var f=d.tail||(d.tail=d.next={});f.callback=b;f.context=c;d.tail=f.next={}}return this},off:function(a,b,c){var d,e,f;if(a){if(e=this._callbacks)for(a=a.split(/\s+/);d=a.shift();)if(f=e[d],delete e[d],b&&f)for(;(f=f.next)&&f.next;)if(!(f.callback===b&&(!c||f.context===c)))this.on(d,f.callback,f.context)}else delete this._callbacks;return this},trigger:function(a){var b,c,d,e;if(!(d=this._callbacks))return this;e=d.all;for((a=a.split(/\s+/)).push(null);b=a.shift();)e&&a.push({next:e.next,tail:e.tail,
event:b}),(c=d[b])&&a.push({next:c.next,tail:c.tail});for(e=s.call(arguments,1);c=a.pop();){b=c.tail;for(d=c.event?[c.event].concat(e):e;(c=c.next)!==b;)c.callback.apply(c.context||this,d)}return this}};g.Events.bind=g.Events.on;g.Events.unbind=g.Events.off;g.Model=function(a,b){var c;a||(a={});b&&b.parse&&(a=this.parse(a));if(c=j(this,"defaults"))a=f.extend({},c,a);b&&b.collection&&(this.collection=b.collection);this.attributes={};this._escapedAttributes={};this.cid=f.uniqueId("c");if(!this.set(a,
{silent:!0}))throw Error("Can't create an invalid model");delete this._changed;this._previousAttributes=f.clone(this.attributes);this.initialize.apply(this,arguments)};f.extend(g.Model.prototype,g.Events,{idAttribute:"id",initialize:function(){},toJSON:function(){return f.clone(this.attributes)},get:function(a){return this.attributes[a]},escape:function(a){var b;if(b=this._escapedAttributes[a])return b;b=this.attributes[a];return this._escapedAttributes[a]=f.escape(null==b?"":""+b)},has:function(a){return null!=
this.attributes[a]},set:function(a,b,c){var d,e;f.isObject(a)||null==a?(d=a,c=b):(d={},d[a]=b);c||(c={});if(!d)return this;d instanceof g.Model&&(d=d.attributes);if(c.unset)for(e in d)d[e]=void 0;if(!this._validate(d,c))return!1;this.idAttribute in d&&(this.id=d[this.idAttribute]);var b=this.attributes,k=this._escapedAttributes,n=this._previousAttributes||{},h=this._setting;this._changed||(this._changed={});this._setting=!0;for(e in d)if(a=d[e],f.isEqual(b[e],a)||delete k[e],c.unset?delete b[e]:b[e]=
a,this._changing&&!f.isEqual(this._changed[e],a)&&(this.trigger("change:"+e,this,a,c),this._moreChanges=!0),delete this._changed[e],!f.isEqual(n[e],a)||f.has(b,e)!=f.has(n,e))this._changed[e]=a;h||(!c.silent&&this.hasChanged()&&this.change(c),this._setting=!1);return this},unset:function(a,b){(b||(b={})).unset=!0;return this.set(a,null,b)},clear:function(a){(a||(a={})).unset=!0;return this.set(f.clone(this.attributes),a)},fetch:function(a){var a=a?f.clone(a):{},b=this,c=a.success;a.success=function(d,
e,f){if(!b.set(b.parse(d,f),a))return!1;c&&c(b,d)};a.error=g.wrapError(a.error,b,a);return(this.sync||g.sync).call(this,"read",this,a)},save:function(a,b,c){var d,e;f.isObject(a)||null==a?(d=a,c=b):(d={},d[a]=b);c=c?f.clone(c):{};c.wait&&(e=f.clone(this.attributes));a=f.extend({},c,{silent:!0});if(d&&!this.set(d,c.wait?a:c))return!1;var k=this,h=c.success;c.success=function(a,b,e){b=k.parse(a,e);c.wait&&(b=f.extend(d||{},b));if(!k.set(b,c))return!1;h?h(k,a):k.trigger("sync",k,a,c)};c.error=g.wrapError(c.error,
k,c);b=this.isNew()?"create":"update";b=(this.sync||g.sync).call(this,b,this,c);c.wait&&this.set(e,a);return b},destroy:function(a){var a=a?f.clone(a):{},b=this,c=a.success,d=function(){b.trigger("destroy",b,b.collection,a)};if(this.isNew())return d();a.success=function(e){a.wait&&d();c?c(b,e):b.trigger("sync",b,e,a)};a.error=g.wrapError(a.error,b,a);var e=(this.sync||g.sync).call(this,"delete",this,a);a.wait||d();return e},url:function(){var a=j(this.collection,"url")||j(this,"urlRoot")||o();return this.isNew()?
a:a+("/"==a.charAt(a.length-1)?"":"/")+encodeURIComponent(this.id)},parse:function(a){return a},clone:function(){return new this.constructor(this.attributes)},isNew:function(){return null==this.id},change:function(a){if(this._changing||!this.hasChanged())return this;this._moreChanges=this._changing=!0;for(var b in this._changed)this.trigger("change:"+b,this,this._changed[b],a);for(;this._moreChanges;)this._moreChanges=!1,this.trigger("change",this,a);this._previousAttributes=f.clone(this.attributes);
delete this._changed;this._changing=!1;return this},hasChanged:function(a){return!arguments.length?!f.isEmpty(this._changed):this._changed&&f.has(this._changed,a)},changedAttributes:function(a){if(!a)return this.hasChanged()?f.clone(this._changed):!1;var b,c=!1,d=this._previousAttributes,e;for(e in a)if(!f.isEqual(d[e],b=a[e]))(c||(c={}))[e]=b;return c},previous:function(a){return!arguments.length||!this._previousAttributes?null:this._previousAttributes[a]},previousAttributes:function(){return f.clone(this._previousAttributes)},
isValid:function(){return!this.validate(this.attributes)},_validate:function(a,b){if(b.silent||!this.validate)return!0;var a=f.extend({},this.attributes,a),c=this.validate(a,b);if(!c)return!0;b&&b.error?b.error(this,c,b):this.trigger("error",this,c,b);return!1}});g.Collection=function(a,b){b||(b={});b.comparator&&(this.comparator=b.comparator);this._reset();this.initialize.apply(this,arguments);a&&this.reset(a,{silent:!0,parse:b.parse})};f.extend(g.Collection.prototype,g.Events,{model:g.Model,initialize:function(){},
toJSON:function(){return this.map(function(a){return a.toJSON()})},add:function(a,b){var c,d,e,g,h,i={},j={};b||(b={});a=f.isArray(a)?a.slice():[a];for(c=0,d=a.length;c<d;c++){if(!(e=a[c]=this._prepareModel(a[c],b)))throw Error("Can't add an invalid model to a collection");if(i[g=e.cid]||this._byCid[g]||null!=(h=e.id)&&(j[h]||this._byId[h]))throw Error("Can't add the same model to a collection twice");i[g]=j[h]=e}for(c=0;c<d;c++)(e=a[c]).on("all",this._onModelEvent,this),this._byCid[e.cid]=e,null!=
e.id&&(this._byId[e.id]=e);this.length+=d;t.apply(this.models,[null!=b.at?b.at:this.models.length,0].concat(a));this.comparator&&this.sort({silent:!0});if(b.silent)return this;for(c=0,d=this.models.length;c<d;c++)if(i[(e=this.models[c]).cid])b.index=c,e.trigger("add",e,this,b);return this},remove:function(a,b){var c,d,e,g;b||(b={});a=f.isArray(a)?a.slice():[a];for(c=0,d=a.length;c<d;c++)if(g=this.getByCid(a[c])||this.get(a[c]))delete this._byId[g.id],delete this._byCid[g.cid],e=this.indexOf(g),this.models.splice(e,
1),this.length--,b.silent||(b.index=e,g.trigger("remove",g,this,b)),this._removeReference(g);return this},get:function(a){return null==a?null:this._byId[null!=a.id?a.id:a]},getByCid:function(a){return a&&this._byCid[a.cid||a]},at:function(a){return this.models[a]},sort:function(a){a||(a={});if(!this.comparator)throw Error("Cannot sort a set without a comparator");var b=f.bind(this.comparator,this);1==this.comparator.length?this.models=this.sortBy(b):this.models.sort(b);a.silent||this.trigger("reset",
this,a);return this},pluck:function(a){return f.map(this.models,function(b){return b.get(a)})},reset:function(a,b){a||(a=[]);b||(b={});for(var c=0,d=this.models.length;c<d;c++)this._removeReference(this.models[c]);this._reset();this.add(a,{silent:!0,parse:b.parse});b.silent||this.trigger("reset",this,b);return this},fetch:function(a){a=a?f.clone(a):{};void 0===a.parse&&(a.parse=!0);var b=this,c=a.success;a.success=function(d,e,f){b[a.add?"add":"reset"](b.parse(d,f),a);c&&c(b,d)};a.error=g.wrapError(a.error,
b,a);return(this.sync||g.sync).call(this,"read",this,a)},create:function(a,b){var c=this,b=b?f.clone(b):{},a=this._prepareModel(a,b);if(!a)return!1;b.wait||c.add(a,b);var d=b.success;b.success=function(e,f){b.wait&&c.add(e,b);d?d(e,f):e.trigger("sync",a,f,b)};a.save(null,b);return a},parse:function(a){return a},chain:function(){return f(this.models).chain()},_reset:function(){this.length=0;this.models=[];this._byId={};this._byCid={}},_prepareModel:function(a,b){a instanceof g.Model?a.collection||
(a.collection=this):(b.collection=this,a=new this.model(a,b),a._validate(a.attributes,b)||(a=!1));return a},_removeReference:function(a){this==a.collection&&delete a.collection;a.off("all",this._onModelEvent,this)},_onModelEvent:function(a,b,c,d){("add"==a||"remove"==a)&&c!=this||("destroy"==a&&this.remove(b,d),b&&a==="change:"+b.idAttribute&&(delete this._byId[b.previous(b.idAttribute)],this._byId[b.id]=b),this.trigger.apply(this,arguments))}});f.each("forEach,each,map,reduce,reduceRight,find,detect,filter,select,reject,every,all,some,any,include,contains,invoke,max,min,sortBy,sortedIndex,toArray,size,first,initial,rest,last,without,indexOf,shuffle,lastIndexOf,isEmpty,groupBy".split(","),
function(a){g.Collection.prototype[a]=function(){return f[a].apply(f,[this.models].concat(f.toArray(arguments)))}});g.Router=function(a){a||(a={});a.routes&&(this.routes=a.routes);this._bindRoutes();this.initialize.apply(this,arguments)};var u=/:\w+/g,v=/\*\w+/g,w=/[-[\]{}()+?.,\\^$|#\s]/g;f.extend(g.Router.prototype,g.Events,{initialize:function(){},route:function(a,b,c){g.history||(g.history=new g.History);f.isRegExp(a)||(a=this._routeToRegExp(a));c||(c=this[b]);g.history.route(a,f.bind(function(d){d=
this._extractParameters(a,d);c&&c.apply(this,d);this.trigger.apply(this,["route:"+b].concat(d));g.history.trigger("route",this,b,d)},this));return this},navigate:function(a,b){g.history.navigate(a,b)},_bindRoutes:function(){if(this.routes){var a=[],b;for(b in this.routes)a.unshift([b,this.routes[b]]);b=0;for(var c=a.length;b<c;b++)this.route(a[b][0],a[b][1],this[a[b][1]])}},_routeToRegExp:function(a){a=a.replace(w,"\\$&").replace(u,"([^/]+)").replace(v,"(.*?)");return RegExp("^"+a+"$")},_extractParameters:function(a,
b){return a.exec(b).slice(1)}});g.History=function(){this.handlers=[];f.bindAll(this,"checkUrl")};var m=/^[#\/]/,x=/msie [\w.]+/,l=!1;f.extend(g.History.prototype,g.Events,{interval:50,getFragment:function(a,b){if(null==a)if(this._hasPushState||b){var a=window.location.pathname,c=window.location.search;c&&(a+=c)}else a=window.location.hash;a=decodeURIComponent(a);a.indexOf(this.options.root)||(a=a.substr(this.options.root.length));return a.replace(m,"")},start:function(a){if(l)throw Error("Backbone.history has already been started");
this.options=f.extend({},{root:"/"},this.options,a);this._wantsHashChange=!1!==this.options.hashChange;this._wantsPushState=!!this.options.pushState;this._hasPushState=!(!this.options.pushState||!window.history||!window.history.pushState);var a=this.getFragment(),b=document.documentMode;if(b=x.exec(navigator.userAgent.toLowerCase())&&(!b||7>=b))this.iframe=h('<iframe src="javascript:0" tabindex="-1" />').hide().appendTo("body")[0].contentWindow,this.navigate(a);this._hasPushState?h(window).bind("popstate",
this.checkUrl):this._wantsHashChange&&"onhashchange"in window&&!b?h(window).bind("hashchange",this.checkUrl):this._wantsHashChange&&(this._checkUrlInterval=setInterval(this.checkUrl,this.interval));this.fragment=a;l=!0;a=window.location;b=a.pathname==this.options.root;if(this._wantsHashChange&&this._wantsPushState&&!this._hasPushState&&!b)return this.fragment=this.getFragment(null,!0),window.location.replace(this.options.root+"#"+this.fragment),!0;this._wantsPushState&&this._hasPushState&&b&&a.hash&&
(this.fragment=a.hash.replace(m,""),window.history.replaceState({},document.title,a.protocol+"//"+a.host+this.options.root+this.fragment));if(!this.options.silent)return this.loadUrl()},stop:function(){h(window).unbind("popstate",this.checkUrl).unbind("hashchange",this.checkUrl);clearInterval(this._checkUrlInterval);l=!1},route:function(a,b){this.handlers.unshift({route:a,callback:b})},checkUrl:function(){var a=this.getFragment();a==this.fragment&&this.iframe&&(a=this.getFragment(this.iframe.location.hash));
if(a==this.fragment||a==decodeURIComponent(this.fragment))return!1;this.iframe&&this.navigate(a);this.loadUrl()||this.loadUrl(window.location.hash)},loadUrl:function(a){var b=this.fragment=this.getFragment(a);return f.any(this.handlers,function(a){if(a.route.test(b))return a.callback(b),!0})},navigate:function(a,b){if(!l)return!1;if(!b||!0===b)b={trigger:b};var c=(a||"").replace(m,"");this.fragment==c||this.fragment==decodeURIComponent(c)||(this._hasPushState?(0!=c.indexOf(this.options.root)&&(c=
this.options.root+c),this.fragment=c,window.history[b.replace?"replaceState":"pushState"]({},document.title,c)):this._wantsHashChange?(this.fragment=c,this._updateHash(window.location,c,b.replace),this.iframe&&c!=this.getFragment(this.iframe.location.hash)&&(b.replace||this.iframe.document.open().close(),this._updateHash(this.iframe.location,c,b.replace))):window.location.assign(this.options.root+a),b.trigger&&this.loadUrl(a))},_updateHash:function(a,b,c){c?a.replace(a.toString().replace(/(javascript:|#).*$/,
"")+"#"+b):a.hash=b}});g.View=function(a){this.cid=f.uniqueId("view");this._configure(a||{});this._ensureElement();this.initialize.apply(this,arguments);this.delegateEvents()};var y=/^(\S+)\s*(.*)$/,p="model,collection,el,id,attributes,className,tagName".split(",");f.extend(g.View.prototype,g.Events,{tagName:"div",$:function(a){return this.$el.find(a)},initialize:function(){},render:function(){return this},remove:function(){this.$el.remove();return this},make:function(a,b,c){a=document.createElement(a);
b&&h(a).attr(b);c&&h(a).html(c);return a},setElement:function(a,b){this.$el=h(a);this.el=this.$el[0];!1!==b&&this.delegateEvents();return this},delegateEvents:function(a){if(a||(a=j(this,"events"))){this.undelegateEvents();for(var b in a){var c=a[b];f.isFunction(c)||(c=this[a[b]]);if(!c)throw Error('Event "'+a[b]+'" does not exist');var d=b.match(y),e=d[1],d=d[2],c=f.bind(c,this),e=e+(".delegateEvents"+this.cid);""===d?this.$el.bind(e,c):this.$el.delegate(d,e,c)}}},undelegateEvents:function(){this.$el.unbind(".delegateEvents"+
this.cid)},_configure:function(a){this.options&&(a=f.extend({},this.options,a));for(var b=0,c=p.length;b<c;b++){var d=p[b];a[d]&&(this[d]=a[d])}this.options=a},_ensureElement:function(){if(this.el)this.setElement(this.el,!1);else{var a=j(this,"attributes")||{};this.id&&(a.id=this.id);this.className&&(a["class"]=this.className);this.setElement(this.make(this.tagName,a),!1)}}});g.Model.extend=g.Collection.extend=g.Router.extend=g.View.extend=function(a,b){var c=z(this,a,b);c.extend=this.extend;return c};
var A={create:"POST",update:"PUT","delete":"DELETE",read:"GET"};g.sync=function(a,b,c){var d=A[a],e={type:d,dataType:"json"};c.url||(e.url=j(b,"url")||o());if(!c.data&&b&&("create"==a||"update"==a))e.contentType="application/json",e.data=JSON.stringify(b.toJSON());g.emulateJSON&&(e.contentType="application/x-www-form-urlencoded",e.data=e.data?{model:e.data}:{});if(g.emulateHTTP&&("PUT"===d||"DELETE"===d))g.emulateJSON&&(e.data._method=d),e.type="POST",e.beforeSend=function(a){a.setRequestHeader("X-HTTP-Method-Override",
d)};"GET"!==e.type&&!g.emulateJSON&&(e.processData=!1);return h.ajax(f.extend(e,c))};g.wrapError=function(a,b,c){return function(d,e){e=d===b?e:d;a?a(b,e,c):b.trigger("error",b,e,c)}};var q=function(){},z=function(a,b,c){var d;d=b&&b.hasOwnProperty("constructor")?b.constructor:function(){a.apply(this,arguments)};f.extend(d,a);q.prototype=a.prototype;d.prototype=new q;b&&f.extend(d.prototype,b);c&&f.extend(d,c);d.prototype.constructor=d;d.__super__=a.prototype;return d},j=function(a,b){return!a||!a[b]?
null:f.isFunction(a[b])?a[b]():a[b]},o=function(){throw Error('A "url" property or function must be specified');}}).call(this);
/*! iScroll v5.1.3 ~ (c) 2008-2014 Matteo Spinelli ~ http://cubiq.org/license */

(function (window, document, Math) {
var rAF = window.requestAnimationFrame  ||
  window.webkitRequestAnimationFrame  ||
  window.mozRequestAnimationFrame   ||
  window.oRequestAnimationFrame   ||
  window.msRequestAnimationFrame    ||
  function (callback) { window.setTimeout(callback, 1000 / 60); };

var utils = (function () {
  var me = {};

  var _elementStyle = document.createElement('div').style;
  var _vendor = (function () {
    var vendors = ['t', 'webkitT', 'MozT', 'msT', 'OT'],
      transform,
      i = 0,
      l = vendors.length;

    for ( ; i < l; i++ ) {
      transform = vendors[i] + 'ransform';
      if ( transform in _elementStyle ) return vendors[i].substr(0, vendors[i].length-1);
    }

    return false;
  })();

  function _prefixStyle (style) {
    if ( _vendor === false ) return false;
    if ( _vendor === '' ) return style;
    return _vendor + style.charAt(0).toUpperCase() + style.substr(1);
  }

  me.getTime = Date.now || function getTime () { return new Date().getTime(); };

  me.extend = function (target, obj) {
    for ( var i in obj ) {
      target[i] = obj[i];
    }
  };

  me.addEvent = function (el, type, fn, capture) {
    el.addEventListener(type, fn, !!capture);
  };

  me.removeEvent = function (el, type, fn, capture) {
    el.removeEventListener(type, fn, !!capture);
  };

  me.prefixPointerEvent = function (pointerEvent) {
    return window.MSPointerEvent ? 
      'MSPointer' + pointerEvent.charAt(9).toUpperCase() + pointerEvent.substr(10):
      pointerEvent;
  };

  me.momentum = function (current, start, time, lowerMargin, wrapperSize, deceleration) {
    var distance = current - start,
      speed = Math.abs(distance) / time,
      destination,
      duration;

    deceleration = deceleration === undefined ? 0.0006 : deceleration;

    destination = current + ( speed * speed ) / ( 2 * deceleration ) * ( distance < 0 ? -1 : 1 );
    duration = speed / deceleration;

    if ( destination < lowerMargin ) {
      destination = wrapperSize ? lowerMargin - ( wrapperSize / 2.5 * ( speed / 8 ) ) : lowerMargin;
      distance = Math.abs(destination - current);
      duration = distance / speed;
    } else if ( destination > 0 ) {
      destination = wrapperSize ? wrapperSize / 2.5 * ( speed / 8 ) : 0;
      distance = Math.abs(current) + destination;
      duration = distance / speed;
    }

    return {
      destination: Math.round(destination),
      duration: duration
    };
  };

  var _transform = _prefixStyle('transform');

  me.extend(me, {
    hasTransform: _transform !== false,
    hasPerspective: _prefixStyle('perspective') in _elementStyle,
    hasTouch: 'ontouchstart' in window,
    hasPointer: window.PointerEvent || window.MSPointerEvent, // IE10 is prefixed
    hasTransition: _prefixStyle('transition') in _elementStyle
  });

  // This should find all Android browsers lower than build 535.19 (both stock browser and webview)
  me.isBadAndroid = /Android /.test(window.navigator.appVersion) && !(/Chrome\/\d/.test(window.navigator.appVersion));

  me.extend(me.style = {}, {
    transform: _transform,
    transitionTimingFunction: _prefixStyle('transitionTimingFunction'),
    transitionDuration: _prefixStyle('transitionDuration'),
    transitionDelay: _prefixStyle('transitionDelay'),
    transformOrigin: _prefixStyle('transformOrigin')
  });

  me.hasClass = function (e, c) {
    var re = new RegExp("(^|\\s)" + c + "(\\s|$)");
    return re.test(e.className);
  };

  me.addClass = function (e, c) {
    if ( me.hasClass(e, c) ) {
      return;
    }

    var newclass = e.className.split(' ');
    newclass.push(c);
    e.className = newclass.join(' ');
  };

  me.removeClass = function (e, c) {
    if ( !me.hasClass(e, c) ) {
      return;
    }

    var re = new RegExp("(^|\\s)" + c + "(\\s|$)", 'g');
    e.className = e.className.replace(re, ' ');
  };

  me.offset = function (el) {
    var left = -el.offsetLeft,
      top = -el.offsetTop;

    // jshint -W084
    while (el = el.offsetParent) {
      left -= el.offsetLeft;
      top -= el.offsetTop;
    }
    // jshint +W084

    return {
      left: left,
      top: top
    };
  };

  me.preventDefaultException = function (el, exceptions) {
    for ( var i in exceptions ) {
      if ( exceptions[i].test(el[i]) ) {
        return true;
      }
    }

    return false;
  };

  me.extend(me.eventType = {}, {
    touchstart: 1,
    touchmove: 1,
    touchend: 1,

    mousedown: 2,
    mousemove: 2,
    mouseup: 2,

    pointerdown: 3,
    pointermove: 3,
    pointerup: 3,

    MSPointerDown: 3,
    MSPointerMove: 3,
    MSPointerUp: 3
  });

  me.extend(me.ease = {}, {
    quadratic: {
      style: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
      fn: function (k) {
        return k * ( 2 - k );
      }
    },
    circular: {
      style: 'cubic-bezier(0.1, 0.57, 0.1, 1)', // Not properly "circular" but this looks better, it should be (0.075, 0.82, 0.165, 1)
      fn: function (k) {
        return Math.sqrt( 1 - ( --k * k ) );
      }
    },
    back: {
      style: 'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
      fn: function (k) {
        var b = 4;
        return ( k = k - 1 ) * k * ( ( b + 1 ) * k + b ) + 1;
      }
    },
    bounce: {
      style: '',
      fn: function (k) {
        if ( ( k /= 1 ) < ( 1 / 2.75 ) ) {
          return 7.5625 * k * k;
        } else if ( k < ( 2 / 2.75 ) ) {
          return 7.5625 * ( k -= ( 1.5 / 2.75 ) ) * k + 0.75;
        } else if ( k < ( 2.5 / 2.75 ) ) {
          return 7.5625 * ( k -= ( 2.25 / 2.75 ) ) * k + 0.9375;
        } else {
          return 7.5625 * ( k -= ( 2.625 / 2.75 ) ) * k + 0.984375;
        }
      }
    },
    elastic: {
      style: '',
      fn: function (k) {
        var f = 0.22,
          e = 0.4;

        if ( k === 0 ) { return 0; }
        if ( k == 1 ) { return 1; }

        return ( e * Math.pow( 2, - 10 * k ) * Math.sin( ( k - f / 4 ) * ( 2 * Math.PI ) / f ) + 1 );
      }
    }
  });

  me.tap = function (e, eventName) {
    var ev = document.createEvent('Event');
    ev.initEvent(eventName, true, true);
    ev.pageX = e.pageX;
    ev.pageY = e.pageY;
    e.target.dispatchEvent(ev);
  };

  me.click = function (e) {
    var target = e.target,
      ev;

    if ( !(/(SELECT|INPUT|TEXTAREA)/i).test(target.tagName) ) {
      ev = document.createEvent('MouseEvents');
      ev.initMouseEvent('click', true, true, e.view, 1,
        target.screenX, target.screenY, target.clientX, target.clientY,
        e.ctrlKey, e.altKey, e.shiftKey, e.metaKey,
        0, null);

      ev._constructed = true;
      target.dispatchEvent(ev);
    }
  };

  return me;
})();

function IScroll (el, options) {
  this.wrapper = typeof el == 'string' ? document.querySelector(el) : el;
  this.scroller = this.wrapper.children[0];
  this.scrollerStyle = this.scroller.style;   // cache style for better performance

  this.options = {

    zoomMin: 1,
    zoomMax: 4, startZoom: 1,

    resizeScrollbars: true,

    mouseWheelSpeed: 20,

    snapThreshold: 0.334,

// INSERT POINT: OPTIONS 

    startX: 0,
    startY: 0,
    scrollY: true,
    directionLockThreshold: 5,
    momentum: true,

    bounce: true,
    bounceTime: 600,
    bounceEasing: '',

    preventDefault: true,
    preventDefaultException: { tagName: /^(INPUT|TEXTAREA|BUTTON|SELECT)$/ },

    HWCompositing: true,
    useTransition: true,
    useTransform: true
  };

  for ( var i in options ) {
    this.options[i] = options[i];
  }

  // Normalize options
  this.translateZ = this.options.HWCompositing && utils.hasPerspective ? ' translateZ(0)' : '';

  this.options.useTransition = utils.hasTransition && this.options.useTransition;
  this.options.useTransform = utils.hasTransform && this.options.useTransform;

  this.options.eventPassthrough = this.options.eventPassthrough === true ? 'vertical' : this.options.eventPassthrough;
  this.options.preventDefault = !this.options.eventPassthrough && this.options.preventDefault;

  // If you want eventPassthrough I have to lock one of the axes
  this.options.scrollY = this.options.eventPassthrough == 'vertical' ? false : this.options.scrollY;
  this.options.scrollX = this.options.eventPassthrough == 'horizontal' ? false : this.options.scrollX;

  // With eventPassthrough we also need lockDirection mechanism
  this.options.freeScroll = this.options.freeScroll && !this.options.eventPassthrough;
  this.options.directionLockThreshold = this.options.eventPassthrough ? 0 : this.options.directionLockThreshold;

  this.options.bounceEasing = typeof this.options.bounceEasing == 'string' ? utils.ease[this.options.bounceEasing] || utils.ease.circular : this.options.bounceEasing;

  this.options.resizePolling = this.options.resizePolling === undefined ? 60 : this.options.resizePolling;

  if ( this.options.tap === true ) {
    this.options.tap = 'tap';
  }

  if ( this.options.shrinkScrollbars == 'scale' ) {
    this.options.useTransition = false;
  }

  this.options.invertWheelDirection = this.options.invertWheelDirection ? -1 : 1;

// INSERT POINT: NORMALIZATION

  // Some defaults  
  this.x = 0;
  this.y = 0;
  this.directionX = 0;
  this.directionY = 0;
  this._events = {};

  this.scale = Math.min(Math.max(this.options.startZoom, this.options.zoomMin), this.options.zoomMax);

// INSERT POINT: DEFAULTS

  this._init();
  this.refresh();

  this.scrollTo(this.options.startX, this.options.startY);
  this.enable();
}

IScroll.prototype = {
  version: '5.1.3',

  _init: function () {
    this._initEvents();

    if ( this.options.zoom ) {
      this._initZoom();
    }

    if ( this.options.scrollbars || this.options.indicators ) {
      this._initIndicators();
    }

    if ( this.options.mouseWheel ) {
      this._initWheel();
    }

    if ( this.options.snap ) {
      this._initSnap();
    }

    if ( this.options.keyBindings ) {
      this._initKeys();
    }

// INSERT POINT: _init

  },

  destroy: function () {
    this._initEvents(true);

    this._execEvent('destroy');
  },

  _transitionEnd: function (e) {
    if ( e.target != this.scroller || !this.isInTransition ) {
      return;
    }

    this._transitionTime();
    if ( !this.resetPosition(this.options.bounceTime) ) {
      this.isInTransition = false;
      this._execEvent('scrollEnd');
    }
  },

  _start: function (e) {
    // React to left mouse button only
    if ( utils.eventType[e.type] != 1 ) {
      if ( e.button !== 0 ) {
        return;
      }
    }

    if ( !this.enabled || (this.initiated && utils.eventType[e.type] !== this.initiated) ) {
      return;
    }

    if ( this.options.preventDefault && !utils.isBadAndroid && !utils.preventDefaultException(e.target, this.options.preventDefaultException) ) {
      e.preventDefault();
    }

    var point = e.touches ? e.touches[0] : e,
      pos;

    this.initiated  = utils.eventType[e.type];
    this.moved    = false;
    this.distX    = 0;
    this.distY    = 0;
    this.directionX = 0;
    this.directionY = 0;
    this.directionLocked = 0;

    this._transitionTime();

    this.startTime = utils.getTime();

    if ( this.options.useTransition && this.isInTransition ) {
      this.isInTransition = false;
      pos = this.getComputedPosition();
      this._translate(Math.round(pos.x), Math.round(pos.y));
      this._execEvent('scrollEnd');
    } else if ( !this.options.useTransition && this.isAnimating ) {
      this.isAnimating = false;
      this._execEvent('scrollEnd');
    }

    this.startX    = this.x;
    this.startY    = this.y;
    this.absStartX = this.x;
    this.absStartY = this.y;
    this.pointX    = point.pageX;
    this.pointY    = point.pageY;

    this._execEvent('beforeScrollStart');
  },

  _move: function (e) {
    if ( !this.enabled || utils.eventType[e.type] !== this.initiated ) {
      return;
    }

    if ( this.options.preventDefault ) {  // increases performance on Android? TODO: check!
      e.preventDefault();
    }

    var point   = e.touches ? e.touches[0] : e,
      deltaX    = point.pageX - this.pointX,
      deltaY    = point.pageY - this.pointY,
      timestamp = utils.getTime(),
      newX, newY,
      absDistX, absDistY;

    this.pointX   = point.pageX;
    this.pointY   = point.pageY;

    this.distX    += deltaX;
    this.distY    += deltaY;
    absDistX    = Math.abs(this.distX);
    absDistY    = Math.abs(this.distY);

    // We need to move at least 10 pixels for the scrolling to initiate
    if ( timestamp - this.endTime > 300 && (absDistX < 10 && absDistY < 10) ) {
      return;
    }

    // If you are scrolling in one direction lock the other
    if ( !this.directionLocked && !this.options.freeScroll ) {
      if ( absDistX > absDistY + this.options.directionLockThreshold ) {
        this.directionLocked = 'h';   // lock horizontally
      } else if ( absDistY >= absDistX + this.options.directionLockThreshold ) {
        this.directionLocked = 'v';   // lock vertically
      } else {
        this.directionLocked = 'n';   // no lock
      }
    }

    if ( this.directionLocked == 'h' ) {
      if ( this.options.eventPassthrough == 'vertical' ) {
        e.preventDefault();
      } else if ( this.options.eventPassthrough == 'horizontal' ) {
        this.initiated = false;
        return;
      }

      deltaY = 0;
    } else if ( this.directionLocked == 'v' ) {
      if ( this.options.eventPassthrough == 'horizontal' ) {
        e.preventDefault();
      } else if ( this.options.eventPassthrough == 'vertical' ) {
        this.initiated = false;
        return;
      }

      deltaX = 0;
    }

    deltaX = this.hasHorizontalScroll ? deltaX : 0;
    deltaY = this.hasVerticalScroll ? deltaY : 0;

    newX = this.x + deltaX;
    newY = this.y + deltaY;

    // Slow down if outside of the boundaries
    if ( newX > 0 || newX < this.maxScrollX ) {
      newX = this.options.bounce ? this.x + deltaX / 3 : newX > 0 ? 0 : this.maxScrollX;
    }
    if ( newY > 0 || newY < this.maxScrollY ) {
      newY = this.options.bounce ? this.y + deltaY / 3 : newY > 0 ? 0 : this.maxScrollY;
    }

    this.directionX = deltaX > 0 ? -1 : deltaX < 0 ? 1 : 0;
    this.directionY = deltaY > 0 ? -1 : deltaY < 0 ? 1 : 0;

    if ( !this.moved ) {
      this._execEvent('scrollStart');
    }

    this.moved = true;

    this._translate(newX, newY);

/* REPLACE START: _move */

    if ( timestamp - this.startTime > 300 ) {
      this.startTime = timestamp;
      this.startX = this.x;
      this.startY = this.y;
    }

/* REPLACE END: _move */

  },

  _end: function (e) {
    if ( !this.enabled || utils.eventType[e.type] !== this.initiated ) {
      return;
    }

    if ( this.options.preventDefault && !utils.preventDefaultException(e.target, this.options.preventDefaultException) ) {
      e.preventDefault();
    }

    var point = e.changedTouches ? e.changedTouches[0] : e,
      momentumX,
      momentumY,
      duration = utils.getTime() - this.startTime,
      newX = Math.round(this.x),
      newY = Math.round(this.y),
      distanceX = Math.abs(newX - this.startX),
      distanceY = Math.abs(newY - this.startY),
      time = 0,
      easing = '';

    this.isInTransition = 0;
    this.initiated = 0;
    this.endTime = utils.getTime();

    // reset if we are outside of the boundaries
    if ( this.resetPosition(this.options.bounceTime) ) {
      return;
    }

    this.scrollTo(newX, newY);  // ensures that the last position is rounded

    // we scrolled less than 10 pixels
    if ( !this.moved ) {
      if ( this.options.tap ) {
        utils.tap(e, this.options.tap);
      }

      if ( this.options.click ) {
        utils.click(e);
      }

      this._execEvent('scrollCancel');
      return;
    }

    if ( this._events.flick && duration < 200 && distanceX < 100 && distanceY < 100 ) {
      this._execEvent('flick');
      return;
    }

    // start momentum animation if needed
    if ( this.options.momentum && duration < 300 ) {
      momentumX = this.hasHorizontalScroll ? utils.momentum(this.x, this.startX, duration, this.maxScrollX, this.options.bounce ? this.wrapperWidth : 0, this.options.deceleration) : { destination: newX, duration: 0 };
      momentumY = this.hasVerticalScroll ? utils.momentum(this.y, this.startY, duration, this.maxScrollY, this.options.bounce ? this.wrapperHeight : 0, this.options.deceleration) : { destination: newY, duration: 0 };
      newX = momentumX.destination;
      newY = momentumY.destination;
      time = Math.max(momentumX.duration, momentumY.duration);
      this.isInTransition = 1;
    }


    if ( this.options.snap ) {
      var snap = this._nearestSnap(newX, newY);
      this.currentPage = snap;
      time = this.options.snapSpeed || Math.max(
          Math.max(
            Math.min(Math.abs(newX - snap.x), 1000),
            Math.min(Math.abs(newY - snap.y), 1000)
          ), 300);
      newX = snap.x;
      newY = snap.y;

      this.directionX = 0;
      this.directionY = 0;
      easing = this.options.bounceEasing;
    }

// INSERT POINT: _end

    if ( newX != this.x || newY != this.y ) {
      // change easing function when scroller goes out of the boundaries
      if ( newX > 0 || newX < this.maxScrollX || newY > 0 || newY < this.maxScrollY ) {
        easing = utils.ease.quadratic;
      }

      this.scrollTo(newX, newY, time, easing);
      return;
    }

    this._execEvent('scrollEnd');
  },

  _resize: function () {
    var that = this;

    clearTimeout(this.resizeTimeout);

    this.resizeTimeout = setTimeout(function () {
      that.refresh();
    }, this.options.resizePolling);
  },

  resetPosition: function (time) {
    var x = this.x,
      y = this.y;

    time = time || 0;

    if ( !this.hasHorizontalScroll || this.x > 0 ) {
      x = 0;
    } else if ( this.x < this.maxScrollX ) {
      x = this.maxScrollX;
    }

    if ( !this.hasVerticalScroll || this.y > 0 ) {
      y = 0;
    } else if ( this.y < this.maxScrollY ) {
      y = this.maxScrollY;
    }

    if ( x == this.x && y == this.y ) {
      return false;
    }

    this.scrollTo(x, y, time, this.options.bounceEasing);

    return true;
  },

  disable: function () {
    this.enabled = false;
  },

  enable: function () {
    this.enabled = true;
  },

  refresh: function () {
    var rf = this.wrapper.offsetHeight;   // Force reflow

    this.wrapperWidth = this.wrapper.clientWidth;
    this.wrapperHeight  = this.wrapper.clientHeight;

/* REPLACE START: refresh */
  this.scrollerWidth  = Math.round(this.scroller.offsetWidth * this.scale);
  this.scrollerHeight = Math.round(this.scroller.offsetHeight * this.scale);

  this.maxScrollX   = this.wrapperWidth - this.scrollerWidth;
  this.maxScrollY   = this.wrapperHeight - this.scrollerHeight;
/* REPLACE END: refresh */

    this.hasHorizontalScroll  = this.options.scrollX && this.maxScrollX < 0;
    this.hasVerticalScroll    = this.options.scrollY && this.maxScrollY < 0;

    if ( !this.hasHorizontalScroll ) {
      this.maxScrollX = 0;
      this.scrollerWidth = this.wrapperWidth;
    }

    if ( !this.hasVerticalScroll ) {
      this.maxScrollY = 0;
      this.scrollerHeight = this.wrapperHeight;
    }

    this.endTime = 0;
    this.directionX = 0;
    this.directionY = 0;

    this.wrapperOffset = utils.offset(this.wrapper);

    this._execEvent('refresh');

    this.resetPosition();

// INSERT POINT: _refresh

  },

  on: function (type, fn) {
    if ( !this._events[type] ) {
      this._events[type] = [];
    }

    this._events[type].push(fn);
  },

  off: function (type, fn) {
    if ( !this._events[type] ) {
      return;
    }

    var index = this._events[type].indexOf(fn);

    if ( index > -1 ) {
      this._events[type].splice(index, 1);
    }
  },

  _execEvent: function (type) {
    if ( !this._events[type] ) {
      return;
    }

    var i = 0,
      l = this._events[type].length;

    if ( !l ) {
      return;
    }

    for ( ; i < l; i++ ) {
      this._events[type][i].apply(this, [].slice.call(arguments, 1));
    }
  },

  scrollBy: function (x, y, time, easing) {
    x = this.x + x;
    y = this.y + y;
    time = time || 0;

    this.scrollTo(x, y, time, easing);
  },

  scrollTo: function (x, y, time, easing) {
    easing = easing || utils.ease.circular;

    this.isInTransition = this.options.useTransition && time > 0;

    if ( !time || (this.options.useTransition && easing.style) ) {
      this._transitionTimingFunction(easing.style);
      this._transitionTime(time);
      this._translate(x, y);
    } else {
      this._animate(x, y, time, easing.fn);
    }
  },

  scrollToElement: function (el, time, offsetX, offsetY, easing) {
    el = el.nodeType ? el : this.scroller.querySelector(el);

    if ( !el ) {
      return;
    }

    var pos = utils.offset(el);

    pos.left -= this.wrapperOffset.left;
    pos.top  -= this.wrapperOffset.top;

    // if offsetX/Y are true we center the element to the screen
    if ( offsetX === true ) {
      offsetX = Math.round(el.offsetWidth / 2 - this.wrapper.offsetWidth / 2);
    }
    if ( offsetY === true ) {
      offsetY = Math.round(el.offsetHeight / 2 - this.wrapper.offsetHeight / 2);
    }

    pos.left -= offsetX || 0;
    pos.top  -= offsetY || 0;

    pos.left = pos.left > 0 ? 0 : pos.left < this.maxScrollX ? this.maxScrollX : pos.left;
    pos.top  = pos.top  > 0 ? 0 : pos.top  < this.maxScrollY ? this.maxScrollY : pos.top;

    time = time === undefined || time === null || time === 'auto' ? Math.max(Math.abs(this.x-pos.left), Math.abs(this.y-pos.top)) : time;

    this.scrollTo(pos.left, pos.top, time, easing);
  },

  _transitionTime: function (time) {
    time = time || 0;

    this.scrollerStyle[utils.style.transitionDuration] = time + 'ms';

    if ( !time && utils.isBadAndroid ) {
      this.scrollerStyle[utils.style.transitionDuration] = '0.001s';
    }


    if ( this.indicators ) {
      for ( var i = this.indicators.length; i--; ) {
        this.indicators[i].transitionTime(time);
      }
    }


// INSERT POINT: _transitionTime

  },

  _transitionTimingFunction: function (easing) {
    this.scrollerStyle[utils.style.transitionTimingFunction] = easing;


    if ( this.indicators ) {
      for ( var i = this.indicators.length; i--; ) {
        this.indicators[i].transitionTimingFunction(easing);
      }
    }


// INSERT POINT: _transitionTimingFunction

  },

  _translate: function (x, y) {
    if ( this.options.useTransform ) {

/* REPLACE START: _translate */     this.scrollerStyle[utils.style.transform] = 'translate(' + x + 'px,' + y + 'px) scale(' + this.scale + ') ' + this.translateZ;/* REPLACE END: _translate */

    } else {
      x = Math.round(x);
      y = Math.round(y);
      this.scrollerStyle.left = x + 'px';
      this.scrollerStyle.top = y + 'px';
    }

    this.x = x;
    this.y = y;


  if ( this.indicators ) {
    for ( var i = this.indicators.length; i--; ) {
      this.indicators[i].updatePosition();
    }
  }


// INSERT POINT: _translate

  },

  _initEvents: function (remove) {
    var eventType = remove ? utils.removeEvent : utils.addEvent,
      target = this.options.bindToWrapper ? this.wrapper : window;

    eventType(window, 'orientationchange', this);
    eventType(window, 'resize', this);

    if ( this.options.click ) {
      eventType(this.wrapper, 'click', this, true);
    }

    if ( !this.options.disableMouse ) {
      eventType(this.wrapper, 'mousedown', this);
      eventType(target, 'mousemove', this);
      eventType(target, 'mousecancel', this);
      eventType(target, 'mouseup', this);
    }

    if ( utils.hasPointer && !this.options.disablePointer ) {
      eventType(this.wrapper, utils.prefixPointerEvent('pointerdown'), this);
      eventType(target, utils.prefixPointerEvent('pointermove'), this);
      eventType(target, utils.prefixPointerEvent('pointercancel'), this);
      eventType(target, utils.prefixPointerEvent('pointerup'), this);
    }

    if ( utils.hasTouch && !this.options.disableTouch ) {
      eventType(this.wrapper, 'touchstart', this);
      eventType(target, 'touchmove', this);
      eventType(target, 'touchcancel', this);
      eventType(target, 'touchend', this);
    }

    eventType(this.scroller, 'transitionend', this);
    eventType(this.scroller, 'webkitTransitionEnd', this);
    eventType(this.scroller, 'oTransitionEnd', this);
    eventType(this.scroller, 'MSTransitionEnd', this);
  },

  getComputedPosition: function () {
    var matrix = window.getComputedStyle(this.scroller, null),
      x, y;

    if ( this.options.useTransform ) {
      matrix = matrix[utils.style.transform].split(')')[0].split(', ');
      x = +(matrix[12] || matrix[4]);
      y = +(matrix[13] || matrix[5]);
    } else {
      x = +matrix.left.replace(/[^-\d.]/g, '');
      y = +matrix.top.replace(/[^-\d.]/g, '');
    }

    return { x: x, y: y };
  },

  _initIndicators: function () {
    var interactive = this.options.interactiveScrollbars,
      customStyle = typeof this.options.scrollbars != 'string',
      indicators = [],
      indicator;

    var that = this;

    this.indicators = [];

    if ( this.options.scrollbars ) {
      // Vertical scrollbar
      if ( this.options.scrollY ) {
        indicator = {
          el: createDefaultScrollbar('v', interactive, this.options.scrollbars),
          interactive: interactive,
          defaultScrollbars: true,
          customStyle: customStyle,
          resize: this.options.resizeScrollbars,
          shrink: this.options.shrinkScrollbars,
          fade: this.options.fadeScrollbars,
          listenX: false
        };

        this.wrapper.appendChild(indicator.el);
        indicators.push(indicator);
      }

      // Horizontal scrollbar
      if ( this.options.scrollX ) {
        indicator = {
          el: createDefaultScrollbar('h', interactive, this.options.scrollbars),
          interactive: interactive,
          defaultScrollbars: true,
          customStyle: customStyle,
          resize: this.options.resizeScrollbars,
          shrink: this.options.shrinkScrollbars,
          fade: this.options.fadeScrollbars,
          listenY: false
        };

        this.wrapper.appendChild(indicator.el);
        indicators.push(indicator);
      }
    }

    if ( this.options.indicators ) {
      // TODO: check concat compatibility
      indicators = indicators.concat(this.options.indicators);
    }

    for ( var i = indicators.length; i--; ) {
      this.indicators.push( new Indicator(this, indicators[i]) );
    }

    // TODO: check if we can use array.map (wide compatibility and performance issues)
    function _indicatorsMap (fn) {
      for ( var i = that.indicators.length; i--; ) {
        fn.call(that.indicators[i]);
      }
    }

    if ( this.options.fadeScrollbars ) {
      this.on('scrollEnd', function () {
        _indicatorsMap(function () {
          this.fade();
        });
      });

      this.on('scrollCancel', function () {
        _indicatorsMap(function () {
          this.fade();
        });
      });

      this.on('scrollStart', function () {
        _indicatorsMap(function () {
          this.fade(1);
        });
      });

      this.on('beforeScrollStart', function () {
        _indicatorsMap(function () {
          this.fade(1, true);
        });
      });
    }


    this.on('refresh', function () {
      _indicatorsMap(function () {
        this.refresh();
      });
    });

    this.on('destroy', function () {
      _indicatorsMap(function () {
        this.destroy();
      });

      delete this.indicators;
    });
  },

  _initZoom: function () {
    this.scrollerStyle[utils.style.transformOrigin] = '0 0';
  },

  _zoomStart: function (e) {
    var c1 = Math.abs( e.touches[0].pageX - e.touches[1].pageX ),
      c2 = Math.abs( e.touches[0].pageY - e.touches[1].pageY );

    this.touchesDistanceStart = Math.sqrt(c1 * c1 + c2 * c2);
    this.startScale = this.scale;

    this.originX = Math.abs(e.touches[0].pageX + e.touches[1].pageX) / 2 + this.wrapperOffset.left - this.x;
    this.originY = Math.abs(e.touches[0].pageY + e.touches[1].pageY) / 2 + this.wrapperOffset.top - this.y;

    this._execEvent('zoomStart');
  },

  _zoom: function (e) {
    if ( !this.enabled || utils.eventType[e.type] !== this.initiated ) {
      return;
    }

    if ( this.options.preventDefault ) {
      e.preventDefault();
    }

    var c1 = Math.abs( e.touches[0].pageX - e.touches[1].pageX ),
      c2 = Math.abs( e.touches[0].pageY - e.touches[1].pageY ),
      distance = Math.sqrt( c1 * c1 + c2 * c2 ),
      scale = 1 / this.touchesDistanceStart * distance * this.startScale,
      lastScale,
      x, y;

    this.scaled = true;

    if ( scale < this.options.zoomMin ) {
      scale = 0.5 * this.options.zoomMin * Math.pow(2.0, scale / this.options.zoomMin);
    } else if ( scale > this.options.zoomMax ) {
      scale = 2.0 * this.options.zoomMax * Math.pow(0.5, this.options.zoomMax / scale);
    }

    lastScale = scale / this.startScale;
    x = this.originX - this.originX * lastScale + this.startX;
    y = this.originY - this.originY * lastScale + this.startY;

    this.scale = scale;

    this.scrollTo(x, y, 0);
  },

  _zoomEnd: function (e) {
    if ( !this.enabled || utils.eventType[e.type] !== this.initiated ) {
      return;
    }

    if ( this.options.preventDefault ) {
      e.preventDefault();
    }

    var newX, newY,
      lastScale;

    this.isInTransition = 0;
    this.initiated = 0;

    if ( this.scale > this.options.zoomMax ) {
      this.scale = this.options.zoomMax;
    } else if ( this.scale < this.options.zoomMin ) {
      this.scale = this.options.zoomMin;
    }

    // Update boundaries
    this.refresh();

    lastScale = this.scale / this.startScale;

    newX = this.originX - this.originX * lastScale + this.startX;
    newY = this.originY - this.originY * lastScale + this.startY;

    if ( newX > 0 ) {
      newX = 0;
    } else if ( newX < this.maxScrollX ) {
      newX = this.maxScrollX;
    }

    if ( newY > 0 ) {
      newY = 0;
    } else if ( newY < this.maxScrollY ) {
      newY = this.maxScrollY;
    }

    if ( this.x != newX || this.y != newY ) {
      this.scrollTo(newX, newY, this.options.bounceTime);
    }

    this.scaled = false;

    this._execEvent('zoomEnd');
  },

  zoom: function (scale, x, y, time) {
    if ( scale < this.options.zoomMin ) {
      scale = this.options.zoomMin;
    } else if ( scale > this.options.zoomMax ) {
      scale = this.options.zoomMax;
    }

    if ( scale == this.scale ) {
      return;
    }

    var relScale = scale / this.scale;

    x = x === undefined ? this.wrapperWidth / 2 : x;
    y = y === undefined ? this.wrapperHeight / 2 : y;
    time = time === undefined ? 300 : time;

    x = x + this.wrapperOffset.left - this.x;
    y = y + this.wrapperOffset.top - this.y;

    x = x - x * relScale + this.x;
    y = y - y * relScale + this.y;

    this.scale = scale;

    this.refresh();   // update boundaries

    if ( x > 0 ) {
      x = 0;
    } else if ( x < this.maxScrollX ) {
      x = this.maxScrollX;
    }

    if ( y > 0 ) {
      y = 0;
    } else if ( y < this.maxScrollY ) {
      y = this.maxScrollY;
    }

    this.scrollTo(x, y, time);
  },

  _wheelZoom: function (e) {
    var wheelDeltaY,
      deltaScale,
      that = this;

    // Execute the zoomEnd event after 400ms the wheel stopped scrolling
    clearTimeout(this.wheelTimeout);
    this.wheelTimeout = setTimeout(function () {
      that._execEvent('zoomEnd');
    }, 400);

    if ( 'deltaX' in e ) {
      wheelDeltaY = -e.deltaY / Math.abs(e.deltaY);
    } else if ('wheelDeltaX' in e) {
      wheelDeltaY = e.wheelDeltaY / Math.abs(e.wheelDeltaY);
    } else if('wheelDelta' in e) {
      wheelDeltaY = e.wheelDelta / Math.abs(e.wheelDelta);
    } else if ('detail' in e) {
      wheelDeltaY = -e.detail / Math.abs(e.wheelDelta);
    } else {
      return;
    }

    deltaScale = this.scale + wheelDeltaY / 5;

    this.zoom(deltaScale, e.pageX, e.pageY, 0);
  },

  _initWheel: function () {
    utils.addEvent(this.wrapper, 'wheel', this);
    utils.addEvent(this.wrapper, 'mousewheel', this);
    utils.addEvent(this.wrapper, 'DOMMouseScroll', this);

    this.on('destroy', function () {
      utils.removeEvent(this.wrapper, 'wheel', this);
      utils.removeEvent(this.wrapper, 'mousewheel', this);
      utils.removeEvent(this.wrapper, 'DOMMouseScroll', this);
    });
  },

  _wheel: function (e) {
    if ( !this.enabled ) {
      return;
    }

    e.preventDefault();
    e.stopPropagation();

    var wheelDeltaX, wheelDeltaY,
      newX, newY,
      that = this;

    if ( this.wheelTimeout === undefined ) {
      that._execEvent('scrollStart');
    }

    // Execute the scrollEnd event after 400ms the wheel stopped scrolling
    clearTimeout(this.wheelTimeout);
    this.wheelTimeout = setTimeout(function () {
      that._execEvent('scrollEnd');
      that.wheelTimeout = undefined;
    }, 400);

    if ( 'deltaX' in e ) {
      if (e.deltaMode === 1) {
        wheelDeltaX = -e.deltaX * this.options.mouseWheelSpeed;
        wheelDeltaY = -e.deltaY * this.options.mouseWheelSpeed;
      } else {
        wheelDeltaX = -e.deltaX;
        wheelDeltaY = -e.deltaY;
      }
    } else if ( 'wheelDeltaX' in e ) {
      wheelDeltaX = e.wheelDeltaX / 120 * this.options.mouseWheelSpeed;
      wheelDeltaY = e.wheelDeltaY / 120 * this.options.mouseWheelSpeed;
    } else if ( 'wheelDelta' in e ) {
      wheelDeltaX = wheelDeltaY = e.wheelDelta / 120 * this.options.mouseWheelSpeed;
    } else if ( 'detail' in e ) {
      wheelDeltaX = wheelDeltaY = -e.detail / 3 * this.options.mouseWheelSpeed;
    } else {
      return;
    }

    wheelDeltaX *= this.options.invertWheelDirection;
    wheelDeltaY *= this.options.invertWheelDirection;

    if ( !this.hasVerticalScroll ) {
      wheelDeltaX = wheelDeltaY;
      wheelDeltaY = 0;
    }

    if ( this.options.snap ) {
      newX = this.currentPage.pageX;
      newY = this.currentPage.pageY;

      if ( wheelDeltaX > 0 ) {
        newX--;
      } else if ( wheelDeltaX < 0 ) {
        newX++;
      }

      if ( wheelDeltaY > 0 ) {
        newY--;
      } else if ( wheelDeltaY < 0 ) {
        newY++;
      }

      this.goToPage(newX, newY);

      return;
    }

    newX = this.x + Math.round(this.hasHorizontalScroll ? wheelDeltaX : 0);
    newY = this.y + Math.round(this.hasVerticalScroll ? wheelDeltaY : 0);

    if ( newX > 0 ) {
      newX = 0;
    } else if ( newX < this.maxScrollX ) {
      newX = this.maxScrollX;
    }

    if ( newY > 0 ) {
      newY = 0;
    } else if ( newY < this.maxScrollY ) {
      newY = this.maxScrollY;
    }

    this.scrollTo(newX, newY, 0);

// INSERT POINT: _wheel
  },

  _initSnap: function () {
    this.currentPage = {};

    if ( typeof this.options.snap == 'string' ) {
      this.options.snap = this.scroller.querySelectorAll(this.options.snap);
    }

    this.on('refresh', function () {
      var i = 0, l,
        m = 0, n,
        cx, cy,
        x = 0, y,
        stepX = this.options.snapStepX || this.wrapperWidth,
        stepY = this.options.snapStepY || this.wrapperHeight,
        el;

      this.pages = [];

      if ( !this.wrapperWidth || !this.wrapperHeight || !this.scrollerWidth || !this.scrollerHeight ) {
        return;
      }

      if ( this.options.snap === true ) {
        cx = Math.round( stepX / 2 );
        cy = Math.round( stepY / 2 );

        while ( x > -this.scrollerWidth ) {
          this.pages[i] = [];
          l = 0;
          y = 0;

          while ( y > -this.scrollerHeight ) {
            this.pages[i][l] = {
              x: Math.max(x, this.maxScrollX),
              y: Math.max(y, this.maxScrollY),
              width: stepX,
              height: stepY,
              cx: x - cx,
              cy: y - cy
            };

            y -= stepY;
            l++;
          }

          x -= stepX;
          i++;
        }
      } else {
        el = this.options.snap;
        l = el.length;
        n = -1;

        for ( ; i < l; i++ ) {
          if ( i === 0 || el[i].offsetLeft <= el[i-1].offsetLeft ) {
            m = 0;
            n++;
          }

          if ( !this.pages[m] ) {
            this.pages[m] = [];
          }

          x = Math.max(-el[i].offsetLeft, this.maxScrollX);
          y = Math.max(-el[i].offsetTop, this.maxScrollY);
          cx = x - Math.round(el[i].offsetWidth / 2);
          cy = y - Math.round(el[i].offsetHeight / 2);

          this.pages[m][n] = {
            x: x,
            y: y,
            width: el[i].offsetWidth,
            height: el[i].offsetHeight,
            cx: cx,
            cy: cy
          };

          if ( x > this.maxScrollX ) {
            m++;
          }
        }
      }

      this.goToPage(this.currentPage.pageX || 0, this.currentPage.pageY || 0, 0);

      // Update snap threshold if needed
      if ( this.options.snapThreshold % 1 === 0 ) {
        this.snapThresholdX = this.options.snapThreshold;
        this.snapThresholdY = this.options.snapThreshold;
      } else {
        this.snapThresholdX = Math.round(this.pages[this.currentPage.pageX][this.currentPage.pageY].width * this.options.snapThreshold);
        this.snapThresholdY = Math.round(this.pages[this.currentPage.pageX][this.currentPage.pageY].height * this.options.snapThreshold);
      }
    });

    this.on('flick', function () {
      var time = this.options.snapSpeed || Math.max(
          Math.max(
            Math.min(Math.abs(this.x - this.startX), 1000),
            Math.min(Math.abs(this.y - this.startY), 1000)
          ), 300);

      this.goToPage(
        this.currentPage.pageX + this.directionX,
        this.currentPage.pageY + this.directionY,
        time
      );
    });
  },

  _nearestSnap: function (x, y) {
    if ( !this.pages.length ) {
      return { x: 0, y: 0, pageX: 0, pageY: 0 };
    }

    var i = 0,
      l = this.pages.length,
      m = 0;

    // Check if we exceeded the snap threshold
    if ( Math.abs(x - this.absStartX) < this.snapThresholdX &&
      Math.abs(y - this.absStartY) < this.snapThresholdY ) {
      return this.currentPage;
    }

    if ( x > 0 ) {
      x = 0;
    } else if ( x < this.maxScrollX ) {
      x = this.maxScrollX;
    }

    if ( y > 0 ) {
      y = 0;
    } else if ( y < this.maxScrollY ) {
      y = this.maxScrollY;
    }

    for ( ; i < l; i++ ) {
      if ( x >= this.pages[i][0].cx ) {
        x = this.pages[i][0].x;
        break;
      }
    }

    l = this.pages[i].length;

    for ( ; m < l; m++ ) {
      if ( y >= this.pages[0][m].cy ) {
        y = this.pages[0][m].y;
        break;
      }
    }

    if ( i == this.currentPage.pageX ) {
      i += this.directionX;

      if ( i < 0 ) {
        i = 0;
      } else if ( i >= this.pages.length ) {
        i = this.pages.length - 1;
      }

      x = this.pages[i][0].x;
    }

    if ( m == this.currentPage.pageY ) {
      m += this.directionY;

      if ( m < 0 ) {
        m = 0;
      } else if ( m >= this.pages[0].length ) {
        m = this.pages[0].length - 1;
      }

      y = this.pages[0][m].y;
    }

    return {
      x: x,
      y: y,
      pageX: i,
      pageY: m
    };
  },

  goToPage: function (x, y, time, easing) {
    easing = easing || this.options.bounceEasing;

    if ( x >= this.pages.length ) {
      x = this.pages.length - 1;
    } else if ( x < 0 ) {
      x = 0;
    }

    if ( y >= this.pages[x].length ) {
      y = this.pages[x].length - 1;
    } else if ( y < 0 ) {
      y = 0;
    }

    var posX = this.pages[x][y].x,
      posY = this.pages[x][y].y;

    time = time === undefined ? this.options.snapSpeed || Math.max(
      Math.max(
        Math.min(Math.abs(posX - this.x), 1000),
        Math.min(Math.abs(posY - this.y), 1000)
      ), 300) : time;

    this.currentPage = {
      x: posX,
      y: posY,
      pageX: x,
      pageY: y
    };

    this.scrollTo(posX, posY, time, easing);
  },

  next: function (time, easing) {
    var x = this.currentPage.pageX,
      y = this.currentPage.pageY;

    x++;

    if ( x >= this.pages.length && this.hasVerticalScroll ) {
      x = 0;
      y++;
    }

    this.goToPage(x, y, time, easing);
  },

  prev: function (time, easing) {
    var x = this.currentPage.pageX,
      y = this.currentPage.pageY;

    x--;

    if ( x < 0 && this.hasVerticalScroll ) {
      x = 0;
      y--;
    }

    this.goToPage(x, y, time, easing);
  },

  _initKeys: function (e) {
    // default key bindings
    var keys = {
      pageUp: 33,
      pageDown: 34,
      end: 35,
      home: 36,
      left: 37,
      up: 38,
      right: 39,
      down: 40
    };
    var i;

    // if you give me characters I give you keycode
    if ( typeof this.options.keyBindings == 'object' ) {
      for ( i in this.options.keyBindings ) {
        if ( typeof this.options.keyBindings[i] == 'string' ) {
          this.options.keyBindings[i] = this.options.keyBindings[i].toUpperCase().charCodeAt(0);
        }
      }
    } else {
      this.options.keyBindings = {};
    }

    for ( i in keys ) {
      this.options.keyBindings[i] = this.options.keyBindings[i] || keys[i];
    }

    utils.addEvent(window, 'keydown', this);

    this.on('destroy', function () {
      utils.removeEvent(window, 'keydown', this);
    });
  },

  _key: function (e) {
    if ( !this.enabled ) {
      return;
    }

    var snap = this.options.snap, // we are using this alot, better to cache it
      newX = snap ? this.currentPage.pageX : this.x,
      newY = snap ? this.currentPage.pageY : this.y,
      now = utils.getTime(),
      prevTime = this.keyTime || 0,
      acceleration = 0.250,
      pos;

    if ( this.options.useTransition && this.isInTransition ) {
      pos = this.getComputedPosition();

      this._translate(Math.round(pos.x), Math.round(pos.y));
      this.isInTransition = false;
    }

    this.keyAcceleration = now - prevTime < 200 ? Math.min(this.keyAcceleration + acceleration, 50) : 0;

    switch ( e.keyCode ) {
      case this.options.keyBindings.pageUp:
        if ( this.hasHorizontalScroll && !this.hasVerticalScroll ) {
          newX += snap ? 1 : this.wrapperWidth;
        } else {
          newY += snap ? 1 : this.wrapperHeight;
        }
        break;
      case this.options.keyBindings.pageDown:
        if ( this.hasHorizontalScroll && !this.hasVerticalScroll ) {
          newX -= snap ? 1 : this.wrapperWidth;
        } else {
          newY -= snap ? 1 : this.wrapperHeight;
        }
        break;
      case this.options.keyBindings.end:
        newX = snap ? this.pages.length-1 : this.maxScrollX;
        newY = snap ? this.pages[0].length-1 : this.maxScrollY;
        break;
      case this.options.keyBindings.home:
        newX = 0;
        newY = 0;
        break;
      case this.options.keyBindings.left:
        newX += snap ? -1 : 5 + this.keyAcceleration>>0;
        break;
      case this.options.keyBindings.up:
        newY += snap ? 1 : 5 + this.keyAcceleration>>0;
        break;
      case this.options.keyBindings.right:
        newX -= snap ? -1 : 5 + this.keyAcceleration>>0;
        break;
      case this.options.keyBindings.down:
        newY -= snap ? 1 : 5 + this.keyAcceleration>>0;
        break;
      default:
        return;
    }

    if ( snap ) {
      this.goToPage(newX, newY);
      return;
    }

    if ( newX > 0 ) {
      newX = 0;
      this.keyAcceleration = 0;
    } else if ( newX < this.maxScrollX ) {
      newX = this.maxScrollX;
      this.keyAcceleration = 0;
    }

    if ( newY > 0 ) {
      newY = 0;
      this.keyAcceleration = 0;
    } else if ( newY < this.maxScrollY ) {
      newY = this.maxScrollY;
      this.keyAcceleration = 0;
    }

    this.scrollTo(newX, newY, 0);

    this.keyTime = now;
  },

  _animate: function (destX, destY, duration, easingFn) {
    var that = this,
      startX = this.x,
      startY = this.y,
      startTime = utils.getTime(),
      destTime = startTime + duration;

    function step () {
      var now = utils.getTime(),
        newX, newY,
        easing;

      if ( now >= destTime ) {
        that.isAnimating = false;
        that._translate(destX, destY);

        if ( !that.resetPosition(that.options.bounceTime) ) {
          that._execEvent('scrollEnd');
        }

        return;
      }

      now = ( now - startTime ) / duration;
      easing = easingFn(now);
      newX = ( destX - startX ) * easing + startX;
      newY = ( destY - startY ) * easing + startY;
      that._translate(newX, newY);

      if ( that.isAnimating ) {
        rAF(step);
      }
    }

    this.isAnimating = true;
    step();
  },
  handleEvent: function (e) {
    switch ( e.type ) {
      case 'touchstart':
      case 'pointerdown':
      case 'MSPointerDown':
      case 'mousedown':
        this._start(e);

        if ( this.options.zoom && e.touches && e.touches.length > 1 ) {
          this._zoomStart(e);
        }
        break;
      case 'touchmove':
      case 'pointermove':
      case 'MSPointerMove':
      case 'mousemove':
        if ( this.options.zoom && e.touches && e.touches[1] ) {
          this._zoom(e);
          return;
        }
        this._move(e);
        break;
      case 'touchend':
      case 'pointerup':
      case 'MSPointerUp':
      case 'mouseup':
      case 'touchcancel':
      case 'pointercancel':
      case 'MSPointerCancel':
      case 'mousecancel':
        if ( this.scaled ) {
          this._zoomEnd(e);
          return;
        }
        this._end(e);
        break;
      case 'orientationchange':
      case 'resize':
        this._resize();
        break;
      case 'transitionend':
      case 'webkitTransitionEnd':
      case 'oTransitionEnd':
      case 'MSTransitionEnd':
        this._transitionEnd(e);
        break;
      case 'wheel':
      case 'DOMMouseScroll':
      case 'mousewheel':
        if ( this.options.wheelAction == 'zoom' ) {
          this._wheelZoom(e);
          return; 
        }
        this._wheel(e);
        break;
      case 'keydown':
        this._key(e);
        break;
    }
  }

};
function createDefaultScrollbar (direction, interactive, type) {
  var scrollbar = document.createElement('div'),
    indicator = document.createElement('div');

  if ( type === true ) {
    scrollbar.style.cssText = 'position:absolute;z-index:9999';
    indicator.style.cssText = '-webkit-box-sizing:border-box;-moz-box-sizing:border-box;box-sizing:border-box;position:absolute;background:rgba(0,0,0,0.5);border:1px solid rgba(255,255,255,0.9);border-radius:3px';
  }

  indicator.className = 'iScrollIndicator';

  if ( direction == 'h' ) {
    if ( type === true ) {
      scrollbar.style.cssText += ';height:7px;left:2px;right:2px;bottom:0';
      indicator.style.height = '100%';
    }
    scrollbar.className = 'iScrollHorizontalScrollbar';
  } else {
    if ( type === true ) {
      scrollbar.style.cssText += ';width:7px;bottom:2px;top:2px;right:1px';
      indicator.style.width = '100%';
    }
    scrollbar.className = 'iScrollVerticalScrollbar';
  }

  scrollbar.style.cssText += ';overflow:hidden';

  if ( !interactive ) {
    scrollbar.style.pointerEvents = 'none';
  }

  scrollbar.appendChild(indicator);

  return scrollbar;
}

function Indicator (scroller, options) {
  this.wrapper = typeof options.el == 'string' ? document.querySelector(options.el) : options.el;
  this.wrapperStyle = this.wrapper.style;
  this.indicator = this.wrapper.children[0];
  this.indicatorStyle = this.indicator.style;
  this.scroller = scroller;

  this.options = {
    listenX: true,
    listenY: true,
    interactive: false,
    resize: true,
    defaultScrollbars: false,
    shrink: false,
    fade: false,
    speedRatioX: 0,
    speedRatioY: 0
  };

  for ( var i in options ) {
    this.options[i] = options[i];
  }

  this.sizeRatioX = 1;
  this.sizeRatioY = 1;
  this.maxPosX = 0;
  this.maxPosY = 0;

  if ( this.options.interactive ) {
    if ( !this.options.disableTouch ) {
      utils.addEvent(this.indicator, 'touchstart', this);
      utils.addEvent(window, 'touchend', this);
    }
    if ( !this.options.disablePointer ) {
      utils.addEvent(this.indicator, utils.prefixPointerEvent('pointerdown'), this);
      utils.addEvent(window, utils.prefixPointerEvent('pointerup'), this);
    }
    if ( !this.options.disableMouse ) {
      utils.addEvent(this.indicator, 'mousedown', this);
      utils.addEvent(window, 'mouseup', this);
    }
  }

  if ( this.options.fade ) {
    this.wrapperStyle[utils.style.transform] = this.scroller.translateZ;
    this.wrapperStyle[utils.style.transitionDuration] = utils.isBadAndroid ? '0.001s' : '0ms';
    this.wrapperStyle.opacity = '0';
  }
}

Indicator.prototype = {
  handleEvent: function (e) {
    switch ( e.type ) {
      case 'touchstart':
      case 'pointerdown':
      case 'MSPointerDown':
      case 'mousedown':
        this._start(e);
        break;
      case 'touchmove':
      case 'pointermove':
      case 'MSPointerMove':
      case 'mousemove':
        this._move(e);
        break;
      case 'touchend':
      case 'pointerup':
      case 'MSPointerUp':
      case 'mouseup':
      case 'touchcancel':
      case 'pointercancel':
      case 'MSPointerCancel':
      case 'mousecancel':
        this._end(e);
        break;
    }
  },

  destroy: function () {
    if ( this.options.interactive ) {
      utils.removeEvent(this.indicator, 'touchstart', this);
      utils.removeEvent(this.indicator, utils.prefixPointerEvent('pointerdown'), this);
      utils.removeEvent(this.indicator, 'mousedown', this);

      utils.removeEvent(window, 'touchmove', this);
      utils.removeEvent(window, utils.prefixPointerEvent('pointermove'), this);
      utils.removeEvent(window, 'mousemove', this);

      utils.removeEvent(window, 'touchend', this);
      utils.removeEvent(window, utils.prefixPointerEvent('pointerup'), this);
      utils.removeEvent(window, 'mouseup', this);
    }

    if ( this.options.defaultScrollbars ) {
      this.wrapper.parentNode.removeChild(this.wrapper);
    }
  },

  _start: function (e) {
    var point = e.touches ? e.touches[0] : e;

    e.preventDefault();
    e.stopPropagation();

    this.transitionTime();

    this.initiated = true;
    this.moved = false;
    this.lastPointX = point.pageX;
    this.lastPointY = point.pageY;

    this.startTime  = utils.getTime();

    if ( !this.options.disableTouch ) {
      utils.addEvent(window, 'touchmove', this);
    }
    if ( !this.options.disablePointer ) {
      utils.addEvent(window, utils.prefixPointerEvent('pointermove'), this);
    }
    if ( !this.options.disableMouse ) {
      utils.addEvent(window, 'mousemove', this);
    }

    this.scroller._execEvent('beforeScrollStart');
  },

  _move: function (e) {
    var point = e.touches ? e.touches[0] : e,
      deltaX, deltaY,
      newX, newY,
      timestamp = utils.getTime();

    if ( !this.moved ) {
      this.scroller._execEvent('scrollStart');
    }

    this.moved = true;

    deltaX = point.pageX - this.lastPointX;
    this.lastPointX = point.pageX;

    deltaY = point.pageY - this.lastPointY;
    this.lastPointY = point.pageY;

    newX = this.x + deltaX;
    newY = this.y + deltaY;

    this._pos(newX, newY);

// INSERT POINT: indicator._move

    e.preventDefault();
    e.stopPropagation();
  },

  _end: function (e) {
    if ( !this.initiated ) {
      return;
    }

    this.initiated = false;

    e.preventDefault();
    e.stopPropagation();

    utils.removeEvent(window, 'touchmove', this);
    utils.removeEvent(window, utils.prefixPointerEvent('pointermove'), this);
    utils.removeEvent(window, 'mousemove', this);

    if ( this.scroller.options.snap ) {
      var snap = this.scroller._nearestSnap(this.scroller.x, this.scroller.y);

      var time = this.options.snapSpeed || Math.max(
          Math.max(
            Math.min(Math.abs(this.scroller.x - snap.x), 1000),
            Math.min(Math.abs(this.scroller.y - snap.y), 1000)
          ), 300);

      if ( this.scroller.x != snap.x || this.scroller.y != snap.y ) {
        this.scroller.directionX = 0;
        this.scroller.directionY = 0;
        this.scroller.currentPage = snap;
        this.scroller.scrollTo(snap.x, snap.y, time, this.scroller.options.bounceEasing);
      }
    }

    if ( this.moved ) {
      this.scroller._execEvent('scrollEnd');
    }
  },

  transitionTime: function (time) {
    time = time || 0;
    this.indicatorStyle[utils.style.transitionDuration] = time + 'ms';

    if ( !time && utils.isBadAndroid ) {
      this.indicatorStyle[utils.style.transitionDuration] = '0.001s';
    }
  },

  transitionTimingFunction: function (easing) {
    this.indicatorStyle[utils.style.transitionTimingFunction] = easing;
  },

  refresh: function () {
    this.transitionTime();

    if ( this.options.listenX && !this.options.listenY ) {
      this.indicatorStyle.display = this.scroller.hasHorizontalScroll ? 'block' : 'none';
    } else if ( this.options.listenY && !this.options.listenX ) {
      this.indicatorStyle.display = this.scroller.hasVerticalScroll ? 'block' : 'none';
    } else {
      this.indicatorStyle.display = this.scroller.hasHorizontalScroll || this.scroller.hasVerticalScroll ? 'block' : 'none';
    }

    if ( this.scroller.hasHorizontalScroll && this.scroller.hasVerticalScroll ) {
      utils.addClass(this.wrapper, 'iScrollBothScrollbars');
      utils.removeClass(this.wrapper, 'iScrollLoneScrollbar');

      if ( this.options.defaultScrollbars && this.options.customStyle ) {
        if ( this.options.listenX ) {
          this.wrapper.style.right = '8px';
        } else {
          this.wrapper.style.bottom = '8px';
        }
      }
    } else {
      utils.removeClass(this.wrapper, 'iScrollBothScrollbars');
      utils.addClass(this.wrapper, 'iScrollLoneScrollbar');

      if ( this.options.defaultScrollbars && this.options.customStyle ) {
        if ( this.options.listenX ) {
          this.wrapper.style.right = '2px';
        } else {
          this.wrapper.style.bottom = '2px';
        }
      }
    }

    var r = this.wrapper.offsetHeight;  // force refresh

    if ( this.options.listenX ) {
      this.wrapperWidth = this.wrapper.clientWidth;
      if ( this.options.resize ) {
        this.indicatorWidth = Math.max(Math.round(this.wrapperWidth * this.wrapperWidth / (this.scroller.scrollerWidth || this.wrapperWidth || 1)), 8);
        this.indicatorStyle.width = this.indicatorWidth + 'px';
      } else {
        this.indicatorWidth = this.indicator.clientWidth;
      }

      this.maxPosX = this.wrapperWidth - this.indicatorWidth;

      if ( this.options.shrink == 'clip' ) {
        this.minBoundaryX = -this.indicatorWidth + 8;
        this.maxBoundaryX = this.wrapperWidth - 8;
      } else {
        this.minBoundaryX = 0;
        this.maxBoundaryX = this.maxPosX;
      }

      this.sizeRatioX = this.options.speedRatioX || (this.scroller.maxScrollX && (this.maxPosX / this.scroller.maxScrollX));  
    }

    if ( this.options.listenY ) {
      this.wrapperHeight = this.wrapper.clientHeight;
      if ( this.options.resize ) {
        this.indicatorHeight = Math.max(Math.round(this.wrapperHeight * this.wrapperHeight / (this.scroller.scrollerHeight || this.wrapperHeight || 1)), 8);
        this.indicatorStyle.height = this.indicatorHeight + 'px';
      } else {
        this.indicatorHeight = this.indicator.clientHeight;
      }

      this.maxPosY = this.wrapperHeight - this.indicatorHeight;

      if ( this.options.shrink == 'clip' ) {
        this.minBoundaryY = -this.indicatorHeight + 8;
        this.maxBoundaryY = this.wrapperHeight - 8;
      } else {
        this.minBoundaryY = 0;
        this.maxBoundaryY = this.maxPosY;
      }

      this.maxPosY = this.wrapperHeight - this.indicatorHeight;
      this.sizeRatioY = this.options.speedRatioY || (this.scroller.maxScrollY && (this.maxPosY / this.scroller.maxScrollY));
    }

    this.updatePosition();
  },

  updatePosition: function () {
    var x = this.options.listenX && Math.round(this.sizeRatioX * this.scroller.x) || 0,
      y = this.options.listenY && Math.round(this.sizeRatioY * this.scroller.y) || 0;

    if ( !this.options.ignoreBoundaries ) {
      if ( x < this.minBoundaryX ) {
        if ( this.options.shrink == 'scale' ) {
          this.width = Math.max(this.indicatorWidth + x, 8);
          this.indicatorStyle.width = this.width + 'px';
        }
        x = this.minBoundaryX;
      } else if ( x > this.maxBoundaryX ) {
        if ( this.options.shrink == 'scale' ) {
          this.width = Math.max(this.indicatorWidth - (x - this.maxPosX), 8);
          this.indicatorStyle.width = this.width + 'px';
          x = this.maxPosX + this.indicatorWidth - this.width;
        } else {
          x = this.maxBoundaryX;
        }
      } else if ( this.options.shrink == 'scale' && this.width != this.indicatorWidth ) {
        this.width = this.indicatorWidth;
        this.indicatorStyle.width = this.width + 'px';
      }

      if ( y < this.minBoundaryY ) {
        if ( this.options.shrink == 'scale' ) {
          this.height = Math.max(this.indicatorHeight + y * 3, 8);
          this.indicatorStyle.height = this.height + 'px';
        }
        y = this.minBoundaryY;
      } else if ( y > this.maxBoundaryY ) {
        if ( this.options.shrink == 'scale' ) {
          this.height = Math.max(this.indicatorHeight - (y - this.maxPosY) * 3, 8);
          this.indicatorStyle.height = this.height + 'px';
          y = this.maxPosY + this.indicatorHeight - this.height;
        } else {
          y = this.maxBoundaryY;
        }
      } else if ( this.options.shrink == 'scale' && this.height != this.indicatorHeight ) {
        this.height = this.indicatorHeight;
        this.indicatorStyle.height = this.height + 'px';
      }
    }

    this.x = x;
    this.y = y;

    if ( this.scroller.options.useTransform ) {
      this.indicatorStyle[utils.style.transform] = 'translate(' + x + 'px,' + y + 'px)' + this.scroller.translateZ;
    } else {
      this.indicatorStyle.left = x + 'px';
      this.indicatorStyle.top = y + 'px';
    }
  },

  _pos: function (x, y) {
    if ( x < 0 ) {
      x = 0;
    } else if ( x > this.maxPosX ) {
      x = this.maxPosX;
    }

    if ( y < 0 ) {
      y = 0;
    } else if ( y > this.maxPosY ) {
      y = this.maxPosY;
    }

    x = this.options.listenX ? Math.round(x / this.sizeRatioX) : this.scroller.x;
    y = this.options.listenY ? Math.round(y / this.sizeRatioY) : this.scroller.y;

    this.scroller.scrollTo(x, y);
  },

  fade: function (val, hold) {
    if ( hold && !this.visible ) {
      return;
    }

    clearTimeout(this.fadeTimeout);
    this.fadeTimeout = null;

    var time = val ? 250 : 500,
      delay = val ? 0 : 300;

    val = val ? '1' : '0';

    this.wrapperStyle[utils.style.transitionDuration] = time + 'ms';

    this.fadeTimeout = setTimeout((function (val) {
      this.wrapperStyle.opacity = val;
      this.visible = +val;
    }).bind(this, val), delay);
  }
};

IScroll.utils = utils;

if ( typeof module != 'undefined' && module.exports ) {
  module.exports = IScroll;
} else {
  window.IScroll = IScroll;
}

})(window, document, Math);
/*
 * Swipe 2.0
 *
 * Brad Birdsall
 * Copyright 2013, MIT License
 *
*/


/* Modified to allow a 2 finger pinch out to start zoom - dougp */


function Swipe(container, options) {

  "use strict";

  // utilities
  var noop = function() {}; // simple no operation function
  var offloadFn = function(fn) { setTimeout(fn || noop, 0) }; // offload a functions execution
  
  // check browser capabilities
  var browser = {
    addEventListener: !!window.addEventListener,
    touch: ('ontouchstart' in window) || window.DocumentTouch && document instanceof DocumentTouch,
    transitions: (function(temp) {
      var props = ['transitionProperty', 'WebkitTransition', 'MozTransition', 'OTransition', 'msTransition'];
      for ( var i in props ) if (temp.style[ props[i] ] !== undefined) return true;
      return false;
    })(document.createElement('swipe'))
  };

  // quit if no root element
  if (!container) return;
  var element = container.children[0];
  var slides, slidePos, width, length;
  options = options || {};
  var index = parseInt(options.startSlide, 10) || 0;
  var speed = options.speed || 300;
  options.continuous = options.continuous !== undefined ? options.continuous : true;

  function setup() {

    // cache slides
    slides = element.children;
    length = slides.length;

    // set continuous to false if only one slide
    if (slides.length < 2) options.continuous = false;

    //special case if two slides
    if (browser.transitions && options.continuous && slides.length < 3) {
      element.appendChild(slides[0].cloneNode(true));
      element.appendChild(element.children[1].cloneNode(true));
      slides = element.children;
    }

    // create an array to store current positions of each slide
    slidePos = new Array(slides.length);

    // determine width of each slide
    width = container.getBoundingClientRect().width || container.offsetWidth;

    element.style.width = (slides.length * width) + 'px';

    // stack elements
    var pos = slides.length;
    while(pos--) {

      var slide = slides[pos];

      slide.style.width = width + 'px';
      slide.setAttribute('data-index', pos);

      if (browser.transitions) {
        slide.style.left = (pos * -width) + 'px';
        move(pos, index > pos ? -width : (index < pos ? width : 0), 0);
      }

    }

    // reposition elements before and after index
    if (options.continuous && browser.transitions) {
      move(circle(index-1), -width, 0);
      move(circle(index+1), width, 0);
    }

    if (!browser.transitions) element.style.left = (index * -width) + 'px';

    visibleThree(index, slides);

    container.style.visibility = 'visible';

  }

  function prev() {

    if (options.continuous) slide(index-1);
    else if (index) slide(index-1);

  }

  function next() {

    if (options.continuous) slide(index+1);
    else if (index < slides.length - 1) slide(index+1);

  }

  function circle(index) {

    // a simple positive modulo using slides.length
    return (slides.length + (index % slides.length)) % slides.length;

  }

  function slide(to, slideSpeed) {

    // do nothing if already on requested slide
    if (index == to) return;
    
    if (browser.transitions) {

      var direction = Math.abs(index-to) / (index-to); // 1: backward, -1: forward

      // get the actual position of the slide
      if (options.continuous) {
        var natural_direction = direction;
        direction = -slidePos[circle(to)] / width;

        // if going forward but to < index, use to = slides.length + to
        // if going backward but to > index, use to = -slides.length + to
        if (direction !== natural_direction) to =  -direction * slides.length + to;

      }

      var diff = Math.abs(index-to) - 1;

      // move all the slides between index and to in the right direction
      while (diff--) move( circle((to > index ? to : index) - diff - 1), width * direction, 0);
            
      to = circle(to);

      move(index, width * direction, slideSpeed || speed);
      move(to, 0, slideSpeed || speed);

      if (options.continuous) move(circle(to - direction), -(width * direction), 0); // we need to get the next in place
      
    } else {     
      
      to = circle(to);
      animate(index * -width, to * -width, slideSpeed || speed);
      //no fallback for a circular continuous if the browser does not accept transitions
    }

    index = to;

    visibleThree(index, slides);

    offloadFn(options.callback && options.callback(index, slides[index]));
  }

  function move(index, dist, speed) {

    translate(index, dist, speed);
    slidePos[index] = dist;

  }

  function translate(index, dist, speed) {

    var slide = slides[index];
    var style = slide && slide.style;

    if (!style) return;

    style.webkitTransitionDuration = 
    style.MozTransitionDuration = 
    style.msTransitionDuration = 
    style.OTransitionDuration = 
    style.transitionDuration = speed + 'ms';

    style.webkitTransform = 'translate(' + dist + 'px,0)' + 'translateZ(0)';
    style.msTransform = 
    style.MozTransform = 
    style.OTransform = 'translateX(' + dist + 'px)';

  }

  function animate(from, to, speed) {

    // if not an animation, just reposition
    if (!speed) {

      element.style.left = to + 'px';
      return;

    }
    
    var start = +new Date;
    
    var timer = setInterval(function() {

      var timeElap = +new Date - start;
      
      if (timeElap > speed) {

        element.style.left = to + 'px';

        if (delay) begin();

        options.transitionEnd && options.transitionEnd.call(event, index, slides[index]);

        clearInterval(timer);
        return;

      }

      element.style.left = (( (to - from) * (Math.floor((timeElap / speed) * 100) / 100) ) + from) + 'px';

    }, 4);

  }

  // hide all slides then show only current, next and prev
  function visibleThree(index, slides) {

    var pos = slides.length;

    while(pos--) {

      slides[pos].style.visibility = 'hidden';

      if(pos === circle(index) || pos === circle(index-1) || pos === circle(index+1)){
        slides[pos].style.visibility = 'visible';
      }

    }

  }

  // setup auto slideshow
  var delay = options.auto || 0;
  var interval;

  function begin() {

    interval = setTimeout(next, delay);

  }

  function stop() {

    delay = 0;
    clearTimeout(interval);

  }


  // setup initial vars
  var didPopZoom = false;
  var gestureStart;
  var start = {};
  var delta = {};
  var isScrolling;      

  // setup event capturing
  var events = {

    handleEvent: function(event) {

      switch (event.type) {
        case 'gesturechange': this.gesturechange(event); break;
        case 'gesturestart': this.gesturestart(event); break;
        case 'touchstart': this.start(event); break;
        case 'touchmove': this.move(event); break;
        case 'touchend': offloadFn(this.end(event)); break;
        case 'webkitTransitionEnd':
        case 'msTransitionEnd':
        case 'oTransitionEnd':
        case 'otransitionend':
        case 'transitionend': offloadFn(this.transitionEnd(event)); break;
        case 'resize': offloadFn(setup.call()); break;
      }

      if (options.stopPropagation) event.stopPropagation();

    },
    gesturestart: function(e){

      gestureStart = +new Date;
      // if (e.scale > 0.0) {
      //   $(window).trigger('start-zoom');
      // }

    },
    gesturechange: function(e){
    if(popZoomTriggered){
      return;    
    }

      e.preventDefault();
      if (options.disableScroll) e.preventDefault();
      var duration = +new Date - gestureStart;

      var isValidSlide = Number(duration) > 100;
      // console.log(gestureStart);

          
      if (e.scale > 1.0 && isValidSlide) {
        popZoomTriggered = true;
        $(window).trigger('start-zoom'); 
      }
    
      
    },
    start: function(event) {

      var touches = event.touches[0];

      // measure start values
      start = {
        length: event.touches.length,
        // get initial touch coords
        x: touches.pageX,
        y: touches.pageY,

        // store time to determine touch duration
        time: +new Date
      };

      // used for testing first move event
      isScrolling = undefined;

      // reset delta and end measurements
      delta = {};

      // attach touchmove and touchend listeners
      element.addEventListener('touchmove', this, false);
      element.addEventListener('touchend', this, false);

    },
    move: function(event) {



     // measure duration
      // var duration = +new Date - start.time;
      // determine if slide attempt triggers next/prev slide
      // var isValidSlide = 
            // Number(duration) < 250;               // if slide duration is less than 250ms

          // if(start.length > 1 && isValidSlide){
            // $(window).trigger('start-zoom');
            // console.log('stat-zoom');
          // }        


       // Products with one style shouldn't be swipeable. - dougp
       if(options.disableSwipe){
         return; 
       }

      // ensure swiping with one touch and not pinching
      if ( event.touches.length > 1 || event.scale && event.scale !== 1) return

      if (options.disableScroll) event.preventDefault();

      var touches = event.touches[0];

      // measure change in x and y
      delta = {
        x: touches.pageX - start.x,
        y: touches.pageY - start.y
      }

      // determine if scrolling test has run - one time test
      if ( typeof isScrolling == 'undefined') {
        isScrolling = !!( isScrolling || Math.abs(delta.x) < Math.abs(delta.y) );
      }


      // if user is not trying to scroll vertically
      if (!isScrolling) {

        // prevent native scrolling 
        event.preventDefault();


 
        // stop slideshow
        stop();

        // increase resistance if first or last slide
        if (options.continuous) { // we don't add resistance at the end

          translate(circle(index-1), delta.x + slidePos[circle(index-1)], 0);
          translate(index, delta.x + slidePos[index], 0);
          translate(circle(index+1), delta.x + slidePos[circle(index+1)], 0);

        } else {

          delta.x = 
            delta.x / 
              ( (!index && delta.x > 0               // if first slide and sliding left
                || index == slides.length - 1        // or if last slide and sliding right
                && delta.x < 0                       // and if sliding at all
              ) ?                      
              ( Math.abs(delta.x) / width + 1 )      // determine resistance level
              : 1 );                                 // no resistance if false
          
          // translate 1:1
          translate(index-1, delta.x + slidePos[index-1], 0);
          translate(index, delta.x + slidePos[index], 0);
          translate(index+1, delta.x + slidePos[index+1], 0);
        }

      }

    },
    end: function(event) {

      // measure duration
      var duration = +new Date - start.time;

      // determine if slide attempt triggers next/prev slide
      var isValidSlide = 
            Number(duration) < 250               // if slide duration is less than 250ms
            && Math.abs(delta.x) > 20            // and if slide amt is greater than 20px
            || Math.abs(delta.x) > width/2;      // or if slide amt is greater than half the width

      // determine if slide attempt is past start and end
      var isPastBounds = 
            !index && delta.x > 0                            // if first slide and slide amt is greater than 0
            || index == slides.length - 1 && delta.x < 0;    // or if last slide and slide amt is less than 0

      if (options.continuous) isPastBounds = false;
      
      // determine direction of swipe (true:right, false:left)
      var direction = delta.x < 0;

      // if not scrolling vertically
      if (!isScrolling) {

        if (isValidSlide && !isPastBounds) {

          if (direction) {

            if (options.continuous) { // we need to get the next in this direction in place

              move(circle(index-1), -width, 0);
              move(circle(index+2), width, 0);

            } else {
              move(index-1, -width, 0);
            }

            move(index, slidePos[index]-width, speed);
            move(circle(index+1), slidePos[circle(index+1)]-width, speed);
            index = circle(index+1);  
                      
          } else {
            if (options.continuous) { // we need to get the next in this direction in place

              move(circle(index+1), width, 0);
              move(circle(index-2), -width, 0);

            } else {
              move(index+1, width, 0);
            }

            move(index, slidePos[index]+width, speed);
            move(circle(index-1), slidePos[circle(index-1)]+width, speed);
            index = circle(index-1);

          }
          
          visibleThree(index, slides);

          options.callback && options.callback(index, slides[index]);

        } else {

          if (options.continuous) {

            move(circle(index-1), -width, speed);
            move(index, 0, speed);
            move(circle(index+1), width, speed);

          } else {

            move(index-1, -width, speed);
            move(index, 0, speed);
            move(index+1, width, speed);
          }

        }

      }

      // kill touchmove and touchend event listeners until touchstart called again
      element.removeEventListener('touchmove', events, false)
      element.removeEventListener('touchend', events, false)

    },
    transitionEnd: function(event) {

      if (parseInt(event.target.getAttribute('data-index'), 10) == index) {
        
        if (delay) begin();

        options.transitionEnd && options.transitionEnd.call(event, index, slides[index]);

      }

    }

  }

  // trigger setup
  setup();

  // start auto slideshow if applicable
  if (delay) begin();


  // add event listeners
  if (browser.addEventListener) {
    
    // set touchstart event on element    
    if (browser.touch) element.addEventListener('touchstart', events, false);
    if (browser.touch) element.addEventListener('gesturechange', events, false);
    if (browser.touch) element.addEventListener('gesturestart', events, false);

    if (browser.transitions) {
      element.addEventListener('webkitTransitionEnd', events, false);
      element.addEventListener('msTransitionEnd', events, false);
      element.addEventListener('oTransitionEnd', events, false);
      element.addEventListener('otransitionend', events, false);
      element.addEventListener('transitionend', events, false);
    }

    // set resize event on window
    window.addEventListener('resize', events, false);

  } else {

    window.onresize = function () { setup() }; // to play nice with old IE

  }

  // expose the Swipe API
  return {
    setup: function() {

      setup();

    },
    slide: function(to, speed) {
      
      // cancel slideshow
      stop();
      
      slide(to, speed);

    },
    prev: function() {

      // cancel slideshow
      stop();

      prev();

    },
    next: function() {

      // cancel slideshow
      stop();

      next();

    },
    getPos: function() {

      // return current index position
      return index;

    },
    getNumSlides: function() {
      
      // return total number of slides
      return length;
    },
    kill: function() {

      // cancel slideshow
      stop();

      // reset element
      element.style.width = 'auto';
      element.style.left = 0;

      // reset slides
      var pos = slides.length;
      while(pos--) {

        var slide = slides[pos];
        slide.style.width = '100%';
        slide.style.left = 0;

        if (browser.transitions) translate(pos, 0, 0);

      }

      // removed event listeners
      if (browser.addEventListener) {

        // remove current event listeners
        element.removeEventListener('touchstart', events, false);
        element.removeEventListener('webkitTransitionEnd', events, false);
        element.removeEventListener('msTransitionEnd', events, false);
        element.removeEventListener('oTransitionEnd', events, false);
        element.removeEventListener('otransitionend', events, false);
        element.removeEventListener('transitionend', events, false);
        window.removeEventListener('resize', events, false);

      }
      else {

        window.onresize = null;

      }

    }
  }

}


if ( window.jQuery || window.Zepto ) {
  (function($) {
    $.fn.Swipe = function(params) {
      return this.each(function() {
        $(this).data('Swipe', new Swipe($(this)[0], params));
      });
    }
  })( window.jQuery || window.Zepto )
}
;
(function (global, factory) {
  typeof exports === 'object' && typeof module !== 'undefined' ? module.exports = factory() :
  typeof define === 'function' && define.amd ? define(factory) :
  (global.PullToRefresh = factory());
}(this, (function () {

  function _ptrMarkup () { return "\n<div class=\"__PREFIX__box\">\n  <div class=\"__PREFIX__content\">\n    <div class=\"__PREFIX__icon\"></div>\n    <div class=\"__PREFIX__text\"></div>\n  </div>\n</div>"; }

  function _ptrStyles () { return ".__PREFIX__ptr svg { width: 24px; height: 24px; } .__PREFIX__ptr--refresh svg { background: red; width: 24px; height: 24px; } .__PREFIX__ptr {\n pointer-events: none;\n  font-size: 0.85em;\n  font-weight: bold;\n  top: 0;\n  height: 0;\n  transition: height 0.3s, min-height 0.3s, opacity 200ms;\n  text-align: center;\n  width: 100%;\n    align-items: flex-end;\n  align-content: stretch;\n}\n.__PREFIX__box {\n  padding: 10px;\n  flex-basis: 100%;\n}\n.__PREFIX__pull {\n  transition: none;\n}\n.__PREFIX__text {\n  margin-top: 0.33em;\n  color: rgba(0, 0, 0, 0.3);\n}\n.__PREFIX__icon {\n  color: rgba(0, 0, 0, 0.3);\n  transition: transform 0.3s;\n}\n.__PREFIX__top {\n  touch-action: pan-x pan-down pinch-zoom;\n}\n.__PREFIX__release {    \n}\n"; }

  var _defaults = {
    distThreshold: 40,
    distMax: 80,
    distReload: 50,
    distIgnore: 0,
    bodyOffset: 20,
    mainElement: 'body',
    triggerElement: 'body',
    ptrElement: '.ptr',
    classPrefix: 'ptr--',
    cssProp: 'min-height',
    iconArrow: '<?xml version="1.0" encoding="UTF-8"?><svg version="1.1" viewBox="0 0 35 35" xmlns="http://www.w3.org/2000/svg"><g fill="none" fill-rule="evenodd"><g transform="translate(-8 -8)" fill="#000"><path d="m25.5 17c-0.825 0-1.5-0.675-1.5-1.5v-6c0-0.825 0.675-1.5 1.5-1.5s1.5 0.675 1.5 1.5v6c0 0.825-0.675 1.5-1.5 1.5" opacity=".65"/><path d="m29.75 18.139c-0.7145-0.4125-0.9615-1.3345-0.549-2.049l3-5.196c0.4125-0.7145 1.3345-0.9615 2.049-0.549s0.9615 1.3345 0.549 2.049l-3 5.196c-0.4125 0.7145-1.3345 0.9615-2.049 0.549" opacity=".75"/><path d="m32.861 21.25c-0.4125-0.7145-0.1655-1.6365 0.549-2.049l5.196-3c0.7145-0.4125 1.6365-0.1655 2.049 0.549s0.1655 1.6365-0.549 2.049l-5.196 3c-0.7145 0.4125-1.6365 0.1655-2.049-0.549" opacity=".85"/><path d="m34 25.5c0-0.825 0.675-1.5 1.5-1.5h6c0.825 0 1.5 0.675 1.5 1.5s-0.675 1.5-1.5 1.5h-6c-0.825 0-1.5-0.675-1.5-1.5" opacity=".9"/><path d="m32.861 29.75c0.4125-0.7145 1.3345-0.9615 2.049-0.549l5.196 3c0.7145 0.4125 0.9615 1.3345 0.549 2.049s-1.3345 0.9615-2.049 0.549l-5.196-3c-0.7145-0.4125-0.9615-1.3345-0.549-2.049" opacity=".2"/><path d="m29.75 32.861c0.7145-0.4125 1.6365-0.1655 2.049 0.549l3 5.196c0.4125 0.7145 0.1655 1.6365-0.549 2.049s-1.6365 0.1655-2.049-0.549l-3-5.196c-0.4125-0.7145-0.1655-1.6365 0.549-2.049" opacity=".25"/><path d="m25.5 34c0.825 0 1.5 0.675 1.5 1.5v6c0 0.825-0.675 1.5-1.5 1.5s-1.5-0.675-1.5-1.5v-6c0-0.825 0.675-1.5 1.5-1.5" opacity=".3"/><path d="m21.25 32.861c0.7145 0.4125 0.9615 1.3345 0.549 2.049l-3 5.196c-0.4125 0.7145-1.3345 0.9615-2.049 0.549s-0.9615-1.3345-0.549-2.049l3-5.196c0.4125-0.7145 1.3345-0.9615 2.049-0.549" opacity=".35"/><path d="m18.139 29.75c0.4125 0.7145 0.1655 1.6365-0.549 2.049l-5.196 3c-0.7145 0.4125-1.6365 0.1655-2.049-0.549s-0.1655-1.6365 0.549-2.049l5.196-3c0.7145-0.4125 1.6365-0.1655 2.049 0.549" opacity=".4"/><path d="m17 25.5c0 0.825-0.675 1.5-1.5 1.5h-6c-0.825 0-1.5-0.675-1.5-1.5s0.675-1.5 1.5-1.5h6c0.825 0 1.5 0.675 1.5 1.5" opacity=".45"/><path d="m18.139 21.25c-0.4125 0.7145-1.3345 0.9615-2.049 0.549l-5.196-3c-0.7145-0.4125-0.9615-1.3345-0.549-2.049s1.3345-0.9615 2.049-0.549l5.196 3c0.7145 0.4125 0.9615 1.3345 0.549 2.049" opacity=".5"/><path d="m21.25 18.139c-0.7145 0.4125-1.6365 0.1655-2.049-0.549l-3-5.196c-0.4125-0.7145-0.1655-1.6365 0.549-2.049s1.6365-0.1655 2.049 0.549l3 5.196c0.4125 0.7145 0.1655 1.6365-0.549 2.049" opacity=".55"/></g></g></svg>',
    iconRefreshing: '<?xml version="1.0" encoding="UTF-8"?><svg version="1.1" viewBox="0 0 35 35" xmlns="http://www.w3.org/2000/svg"><g fill="none" fill-rule="evenodd"><g transform="translate(-8 -8)" fill="#000"><path d="m25.5 17c-0.825 0-1.5-0.675-1.5-1.5v-6c0-0.825 0.675-1.5 1.5-1.5s1.5 0.675 1.5 1.5v6c0 0.825-0.675 1.5-1.5 1.5" opacity=".65"/><path d="m29.75 18.139c-0.7145-0.4125-0.9615-1.3345-0.549-2.049l3-5.196c0.4125-0.7145 1.3345-0.9615 2.049-0.549s0.9615 1.3345 0.549 2.049l-3 5.196c-0.4125 0.7145-1.3345 0.9615-2.049 0.549" opacity=".75"/><path d="m32.861 21.25c-0.4125-0.7145-0.1655-1.6365 0.549-2.049l5.196-3c0.7145-0.4125 1.6365-0.1655 2.049 0.549s0.1655 1.6365-0.549 2.049l-5.196 3c-0.7145 0.4125-1.6365 0.1655-2.049-0.549" opacity=".85"/><path d="m34 25.5c0-0.825 0.675-1.5 1.5-1.5h6c0.825 0 1.5 0.675 1.5 1.5s-0.675 1.5-1.5 1.5h-6c-0.825 0-1.5-0.675-1.5-1.5" opacity=".9"/><path d="m32.861 29.75c0.4125-0.7145 1.3345-0.9615 2.049-0.549l5.196 3c0.7145 0.4125 0.9615 1.3345 0.549 2.049s-1.3345 0.9615-2.049 0.549l-5.196-3c-0.7145-0.4125-0.9615-1.3345-0.549-2.049" opacity=".2"/><path d="m29.75 32.861c0.7145-0.4125 1.6365-0.1655 2.049 0.549l3 5.196c0.4125 0.7145 0.1655 1.6365-0.549 2.049s-1.6365 0.1655-2.049-0.549l-3-5.196c-0.4125-0.7145-0.1655-1.6365 0.549-2.049" opacity=".25"/><path d="m25.5 34c0.825 0 1.5 0.675 1.5 1.5v6c0 0.825-0.675 1.5-1.5 1.5s-1.5-0.675-1.5-1.5v-6c0-0.825 0.675-1.5 1.5-1.5" opacity=".3"/><path d="m21.25 32.861c0.7145 0.4125 0.9615 1.3345 0.549 2.049l-3 5.196c-0.4125 0.7145-1.3345 0.9615-2.049 0.549s-0.9615-1.3345-0.549-2.049l3-5.196c0.4125-0.7145 1.3345-0.9615 2.049-0.549" opacity=".35"/><path d="m18.139 29.75c0.4125 0.7145 0.1655 1.6365-0.549 2.049l-5.196 3c-0.7145 0.4125-1.6365 0.1655-2.049-0.549s-0.1655-1.6365 0.549-2.049l5.196-3c0.7145-0.4125 1.6365-0.1655 2.049 0.549" opacity=".4"/><path d="m17 25.5c0 0.825-0.675 1.5-1.5 1.5h-6c-0.825 0-1.5-0.675-1.5-1.5s0.675-1.5 1.5-1.5h6c0.825 0 1.5 0.675 1.5 1.5" opacity=".45"/><path d="m18.139 21.25c-0.4125 0.7145-1.3345 0.9615-2.049 0.549l-5.196-3c-0.7145-0.4125-0.9615-1.3345-0.549-2.049s1.3345-0.9615 2.049-0.549l5.196 3c0.7145 0.4125 0.9615 1.3345 0.549 2.049" opacity=".5"/><path d="m21.25 18.139c-0.7145 0.4125-1.6365 0.1655-2.049-0.549l-3-5.196c-0.4125-0.7145-0.1655-1.6365 0.549-2.049s1.6365-0.1655 2.049 0.549l3 5.196c0.4125 0.7145 0.1655 1.6365-0.549 2.049" opacity=".55"/></g></g></svg>',
    instructionsPullToRefresh: '',
    instructionsReleaseToRefresh: '',
    instructionsRefreshing: '',
    refreshTimeout: 500,
    getMarkup: _ptrMarkup,
    getStyles: _ptrStyles,
    onInit: function () {},
    onRefresh: function () { return location.reload(); },
    resistanceFunction: function (t) { return Math.min(1, t / 2.5); },
    shouldPullToRefresh: function () { return !window.scrollY; },
  };

  var _methods = ['mainElement', 'ptrElement', 'triggerElement'];

  var _shared = {
    pullStartY: null,
    pullMoveY: null,
    handlers: [],
    styleEl: null,
    events: null,
    dist: 0,
    state: 'pending',
    timeout: null,
    distResisted: 0,
    supportsPassive: false,
  };

  try {
    window.addEventListener('test', null, {
      get passive() { // eslint-disable-line getter-return
        _shared.supportsPassive = true;
      },
    });
  } catch (e) {
    // do nothing
  }

  var _ptr = {
    setupDOM: function setupDOM(handler) {
      if (!handler.ptrElement) {
        var ptr = document.createElement('div');

        if (handler.mainElement !== document.body) {
          handler.mainElement.parentNode.insertBefore(ptr, handler.mainElement);
        } else {
          document.body.insertBefore(ptr, document.body.firstChild);
        }

        ptr.classList.add(((handler.classPrefix) + "ptr"));
        ptr.innerHTML = handler.getMarkup()
          .replace(/__PREFIX__/g, handler.classPrefix);

        handler.ptrElement = ptr;

        if (typeof handler.onInit === 'function') {
          handler.onInit(handler);
        }

        // Add the css styles to the style node, and then
        // insert it into the dom
        if (!_shared.styleEl) {
          _shared.styleEl = document.createElement('style');
          _shared.styleEl.setAttribute('id', 'pull-to-refresh-js-style');

          document.head.appendChild(_shared.styleEl);
        }

        _shared.styleEl.textContent = handler.getStyles()
          .replace(/__PREFIX__/g, handler.classPrefix)
          .replace(/\s+/g, ' ');
      }

      return handler;
    },
    onReset: function onReset(handler) {
      handler.ptrElement.classList.remove(((handler.classPrefix) + "refresh"));
      handler.ptrElement.style[handler.cssProp] = '0px';

      setTimeout(function () {
        // remove previous ptr-element from DOM
        if (handler.ptrElement && handler.ptrElement.parentNode) {
          handler.ptrElement.parentNode.removeChild(handler.ptrElement);
          handler.ptrElement = null;
        }

        // reset state
        _shared.state = 'pending';
      }, handler.refreshTimeout);
    },
    update: function update(handler) {
      var iconEl = handler.ptrElement.querySelector(("." + (handler.classPrefix) + "icon"));
      var textEl = handler.ptrElement.querySelector(("." + (handler.classPrefix) + "text"));

      if (iconEl) {
        if (_shared.state === 'refreshing') {
          iconEl.innerHTML = handler.iconRefreshing;
        } else {
          iconEl.innerHTML = handler.iconArrow;
        }
      }

      if (textEl) {
        if (_shared.state === 'releasing') {
          textEl.innerHTML = handler.instructionsReleaseToRefresh;
        }

        if (_shared.state === 'pulling' || _shared.state === 'pending') {
          textEl.innerHTML = handler.instructionsPullToRefresh;
        }

        if (_shared.state === 'refreshing') {
          textEl.innerHTML = handler.instructionsRefreshing;
        }
      }
    },
  };

  function _setupEvents() {
    var _el;

    function _onTouchStart(e) {
      // here, we must pick a handler first, and then append their html/css on the DOM
      var target = _shared.handlers.filter(function (h) { return h.contains(e.target); })[0];

      _shared.enable = !!target;

      if (target && _shared.state === 'pending') {
        _el = _ptr.setupDOM(target);

        if (target.shouldPullToRefresh()) {
          _shared.pullStartY = e.touches[0].screenY;
        }

        clearTimeout(_shared.timeout);

        _ptr.update(target);
      }
    }

    function _onTouchMove(e) {
      if (!(_el && _el.ptrElement && _shared.enable)) {
        return;
      }

      if (!_shared.pullStartY) {
        if (_el.shouldPullToRefresh()) {
          _shared.pullStartY = e.touches[0].screenY;
        }
      } else {
        _shared.pullMoveY = e.touches[0].screenY;
      }

      if (_shared.state === 'refreshing') {
        if (_el.shouldPullToRefresh() && _shared.pullStartY < _shared.pullMoveY) {
          e.preventDefault();
        }

        return;
      }

      if (_shared.state === 'pending') {
        _el.ptrElement.classList.add(((_el.classPrefix) + "pull"));
        _shared.state = 'pulling';
        _ptr.update(_el);
      }

      if (_shared.pullStartY && _shared.pullMoveY) {
        _shared.dist = _shared.pullMoveY - _shared.pullStartY;
      }

      _shared.distExtra = _shared.dist - _el.distIgnore;

      if (_shared.distExtra > 0) {
        e.preventDefault();

        _el.ptrElement.style[_el.cssProp] = (_shared.distResisted) + "px";

        _shared.distResisted = _el.resistanceFunction(_shared.distExtra / _el.distThreshold)
          * Math.min(_el.distMax, _shared.distExtra);

        if (_shared.state === 'pulling' && _shared.distResisted > _el.distThreshold) {
          _el.ptrElement.classList.add(((_el.classPrefix) + "release"));
          _shared.state = 'releasing';
          _ptr.update(_el);
        }

        if (_shared.state === 'releasing' && _shared.distResisted < _el.distThreshold) {
          _el.ptrElement.classList.remove(((_el.classPrefix) + "release"));
          _shared.state = 'pulling';
          _ptr.update(_el);
        }
      }
    }

    function _onTouchEnd() {
      if (!(_el && _el.ptrElement && _shared.enable)) {
        return;
      }

      if (_shared.state === 'releasing' && _shared.distResisted > _el.distThreshold) {
        _shared.state = 'refreshing';

        _el.ptrElement.style[_el.cssProp] = (_el.distReload) + "px";
        _el.ptrElement.classList.add(((_el.classPrefix) + "refresh"));

        _shared.timeout = setTimeout(function () {
          var retval = _el.onRefresh(function () { return _ptr.onReset(_el); });

          if (retval && typeof retval.then === 'function') {
            retval.then(function () { return _ptr.onReset(_el); });
          }

          if (!retval && !_el.onRefresh.length) {
            _ptr.onReset(_el);
          }
        }, _el.refreshTimeout);
      } else {
        if (_shared.state === 'refreshing') {
          return;
        }

        _el.ptrElement.style[_el.cssProp] = '0px';

        _shared.state = 'pending';
      }

      _ptr.update(_el);

      _el.ptrElement.classList.remove(((_el.classPrefix) + "release"));
      _el.ptrElement.classList.remove(((_el.classPrefix) + "pull"));

      _shared.pullStartY = _shared.pullMoveY = null;
      _shared.dist = _shared.distResisted = 0;
    }

    function _onScroll() {
      if (_el) {
        _el.mainElement.classList.toggle(((_el.classPrefix) + "top"), _el.shouldPullToRefresh());
      }
    }

    var _passiveSettings = _shared.supportsPassive
      ? { passive: _shared.passive || false }
      : undefined;

    window.addEventListener('touchend', _onTouchEnd);
    window.addEventListener('touchstart', _onTouchStart);
    window.addEventListener('touchmove', _onTouchMove, _passiveSettings);
    window.addEventListener('scroll', _onScroll);

    return {
      onTouchEnd: _onTouchEnd,
      onTouchStart: _onTouchStart,
      onTouchMove: _onTouchMove,
      onScroll: _onScroll,

      destroy: function destroy() {
        // Teardown event listeners
        window.removeEventListener('touchstart', _onTouchStart);
        window.removeEventListener('touchend', _onTouchEnd);
        window.removeEventListener('touchmove', _onTouchMove, _passiveSettings);
        window.removeEventListener('scroll', _onScroll);
      },
    };
  }

  function _setupHandler(options) {
    var _handler = {};

    // merge options with defaults
    Object.keys(_defaults).forEach(function (key) {
      _handler[key] = options[key] || _defaults[key];
    });

    // normalize timeout value, even if it is zero
    _handler.refreshTimeout = typeof options.refreshTimeout === 'number'
      ? options.refreshTimeout
      : _defaults.refreshTimeout;

    // normalize elements
    _methods.forEach(function (method) {
      if (typeof _handler[method] === 'string') {
        _handler[method] = document.querySelector(_handler[method]);
      }
    });

    // attach events lazily
    if (!_shared.events) {
      _shared.events = _setupEvents();
    }

    _handler.contains = function (target) {
      return _handler.triggerElement.contains(target);
    };

    _handler.destroy = function () {
      // stop pending any pending callbacks
      clearTimeout(_shared.timeout);

      // remove handler from shared state
      _shared.handlers.splice(_handler.offset, 1);
    };

    return _handler;
  }

  // public API
  var index = {
    setPassiveMode: function setPassiveMode(isPassive) {
      _shared.passive = isPassive;
    },
    destroyAll: function destroyAll() {
      if (_shared.events) {
        _shared.events.destroy();
        _shared.events = null;
      }

      _shared.handlers.forEach(function (h) {
        h.destroy();
      });
    },
    init: function init(options) {
      if ( options === void 0 ) options = {};

      var handler = _setupHandler(options);

      // store offset for later unsubscription
      handler.offset = _shared.handlers.push(handler) - 1;

      return handler;
    },

    // export utils for testing
    _: {
      setupHandler: _setupHandler,
      setupEvents: _setupEvents,
      setupDOM: _ptr.setupDOM,
      onReset: _ptr.onReset,
      update: _ptr.update,
    },
  };

  return index;

})));
(function($){
  function trim(el) {
    return (''.trim) ? el.val().trim() : $.trim(el.val());
  }
  $.fn.isHappy = function (config) {
    var fields = [], item;
    
    function getError(error) {
      
      var msg;
      if(isFunction(error.message)){
        msg = error.message.call(); // allow callbacks for message text.
      } else {
        msg = error.message;
      }
      return $('<span id="'+error.id+'" class="inline-js-message">'+msg+'</span>');
    }
    function handleSubmit() {
      var errors = false, i, l;
      for (i = 0, l = fields.length; i < l; i += 1) {
        if (!fields[i].testValid(true)) {
          errors = true;
        }
      }
      if (errors) {
        if (isFunction(config.unHappy)) config.unHappy();
        return false;
      } else if (config.testMode) {
        if (window.console) console.warn('would have submitted');
        return false;
      }
    }
    function isFunction (obj) {
      return !!(obj && obj.constructor && obj.call && obj.apply);
    }
    function processField(opts, selector) {
      
      var field = $(selector, config.selectorScope);

      fields.push(field);
      
      field.testValid = function (submit) {
        var error = {
          message: opts.message,
          id: selector.slice(1) + '_unhappy'
        },
        errorEl = getError(error),
        errorSelector = '#' + error.id;
        

        var val,
          el = $(this),
          gotFunc,
          error = false,
          temp, 
          required = !!el.get(0).attributes.getNamedItem('required') || opts.required,
          password = (field.attr('type') === 'password'),
          arg = isFunction(opts.arg) ? opts.arg() : opts.arg;

        // clean it or trim it
        if (isFunction(opts.clean)) {
          val = opts.clean(el.val());
        } else if (!opts.trim && !password) {
          val = trim(el);
        } else {
          val = el.val();
        }

        // write it back to the field
        el.val(val);
        
        // get the value
        // gotFunc = ((val.length > 0 || required === 'sometimes') && isFunction(opts.test));
        gotFunc = (isFunction(opts.test));        
        
        // check if we've got an error on our hands
        
        if(el.attr('type') != 'checkbox'){ // the standard rules don't apply to checkboxes.
          if (required === true && val.length === 0) {
            error = true;
          } else if (gotFunc) {
            error = !opts.test(val, arg);
          }          
        } else {
          if(required == true && el.prop('checked')){
            error = false;
          } else {
            error = true;
          }
        }

        var existingEl = $(errorSelector);

        var doReplace = false;
        if(existingEl.length > 0)
          doReplace = true;

        if (error) {
          if(opts.errorPosition){ // allow for some custom positoning.
            el.addClass('unhappy');
            if(opts.errorPosition.placement == 'append')
              if(doReplace){
                existingEl.html(opts.message);
              } else {
                $(opts.errorPosition.selector).append(errorEl)
              }
          } else {
            if(doReplace){
              existingEl.html(opts.message);
            } else {
              el.addClass('unhappy').after(errorEl);  
            }
          }            
          
          el.closest('.field').addClass('unhappy');
          
          return false;
        } else {
          temp = errorEl.get(0);
          // this is for zepto
          if (temp.parentNode) {
            temp.parentNode.removeChild(temp);
          }
          el.removeClass('unhappy');
          el.closest('.field').removeClass('unhappy');
          el.closest('tr').find('.inline-js-message').remove();
          return true;
        }
      };

      if(field.attr('type') == 'checkbox'){
        field.bind('change', field.testValid)        
      } else {
        field.bind(config.when || 'blur', field.testValid);
      }
      // // any checkboxes? blur doesn't work on t
      // var checkboxes = _.detect(field, function(f){
      //   return $(f).attr('type') == 'checkbox';
      // });

      // field.bind('changed', function(){ // only validate an empty thing on blur if it's been changed.
      //   $(this).data('changed', 1);
      // })
    }
    
    for (item in config.fields) {
      processField(config.fields[item], item);
    }
    
    if (config.submitButton) {
      $(config.submitButton).click(handleSubmit);
    } else {
      this.bind('submit', handleSubmit);
    }
    return this;
  };
})(this.jQuery || this.Zepto);
(function(factory) {
  /* global define */
  /* istanbul ignore next */
  if ( typeof define === 'function' && define.amd ) {
    define(['jquery'], factory);
  } else if ( typeof module === 'object' && module.exports ) {
    // Node/CommonJS
    module.exports = function( root, Zepto ) {
      factory(Zepto);
      return Zepto;
    };
  } else {
    // Browser globals
    factory(Zepto);
  }
}(function($) {
  'use strict';

  var $doc = $(document);
  var $win = $(window);

  var pluginName = 'selectric';
  var classList = 'Input Items Open Disabled TempShow HideSelect Wrapper Focus Hover Responsive Above Scroll Group GroupLabel';
  var eventNamespaceSuffix = '.sl';

  var chars = ['a', 'e', 'i', 'o', 'u', 'n', 'c', 'y'];
  var diacritics = [
    /[\xE0-\xE5]/g, // a
    /[\xE8-\xEB]/g, // e
    /[\xEC-\xEF]/g, // i
    /[\xF2-\xF6]/g, // o
    /[\xF9-\xFC]/g, // u
    /[\xF1]/g,      // n
    /[\xE7]/g,      // c
    /[\xFD-\xFF]/g  // y
  ];

  /**
   * Create an instance of Selectric
   *
   * @constructor
   * @param {Node} element - The &lt;select&gt; element
   * @param {object}  opts - Options
   */
  var Selectric = function(element, opts) {
    var _this = this;

    _this.element = element;
    _this.$element = $(element);

    _this.state = {
      multiple       : !!_this.$element.attr('multiple'),
      enabled        : false,
      opened         : false,
      currValue      : -1,
      selectedIdx    : -1,
      highlightedIdx : -1
    };

    _this.eventTriggers = {
      open    : _this.open,
      close   : _this.close,
      destroy : _this.destroy,
      refresh : _this.refresh,
      init    : _this.init
    };

    _this.init(opts);
  };

  Selectric.prototype = {
    utils: {
      /**
       * Detect mobile browser
       *
       * @return {boolean}
       */
      isMobile: function() {
        return /android|ip(hone|od|ad)/i.test(navigator.userAgent);
      },

      /**
       * Escape especial characters in string (https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions)
       *
       * @param  {string} str - The string to be escaped
       * @return {string}       The string with the special characters escaped
       */
      escapeRegExp: function(str) {
        return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // $& means the whole matched string
      },

      /**
       * Replace diacritics
       *
       * @param  {string} str - The string to replace the diacritics
       * @return {string}       The string with diacritics replaced with ascii characters
       */
      replaceDiacritics: function(str) {
        var k = diacritics.length;

        while (k--) {
          str = str.toLowerCase().replace(diacritics[k], chars[k]);
        }

        return str;
      },

      /**
       * Format string
       * https://gist.github.com/atesgoral/984375
       *
       * @param  {string} f - String to be formated
       * @return {string}     String formated
       */
      format: function(f) {
        var a = arguments; // store outer arguments
        return ('' + f) // force format specifier to String
          .replace( // replace tokens in format specifier
            /\{(?:(\d+)|(\w+))\}/g, // match {token} references
            function(
              s, // the matched string (ignored)
              i, // an argument index
              p // a property name
            ) {
              return p && a[1] // if property name and first argument exist
                ? a[1][p] // return property from first argument
                : a[i]; // assume argument index and return i-th argument
            });
      },

      /**
       * Get the next enabled item in the options list.
       *
       * @param  {object} selectItems - The options object.
       * @param  {number}    selected - Index of the currently selected option.
       * @return {object}               The next enabled item.
       */
      nextEnabledItem: function(selectItems, selected) {
        while ( selectItems[ selected = (selected + 1) % selectItems.length ].disabled ) {
          // empty
        }
        return selected;
      },

      /**
       * Get the previous enabled item in the options list.
       *
       * @param  {object} selectItems - The options object.
       * @param  {number}    selected - Index of the currently selected option.
       * @return {object}               The previous enabled item.
       */
      previousEnabledItem: function(selectItems, selected) {
        while ( selectItems[ selected = (selected > 0 ? selected : selectItems.length) - 1 ].disabled ) {
          // empty
        }
        return selected;
      },

      /**
       * Transform camelCase string to dash-case.
       *
       * @param  {string} str - The camelCased string.
       * @return {string}       The string transformed to dash-case.
       */
      toDash: function(str) {
        return str.replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase();
      },

      /**
       * Calls the events registered with function name.
       *
       * @param {string}    fn - The name of the function.
       * @param {number} scope - Scope that should be set on the function.
       */
      triggerCallback: function(fn, scope) {
        var elm = scope.element;
        var func = scope.options['on' + fn];
        var args = [elm].concat([].slice.call(arguments).slice(1));

        if ( $.isFunction(func) ) {
          func.apply(elm, args);
        }

        $(elm).trigger(pluginName + '-' + this.toDash(fn), args);
      },

      /**
       * Transform array list to concatenated string and remove empty values
       * @param  {array} arr - Class list
       * @return {string}      Concatenated string
       */
      arrayToClassname: function(arr) {
        var newArr = $.grep(arr, function(item) {
          return !!item;
        });

        return $.trim(newArr.join(' '));
      }
    },

    /** Initializes */
    init: function(opts) {
      var _this = this;

      // Set options
      _this.options = $.extend(true, {}, $.fn[pluginName].defaults, _this.options, opts);

      _this.utils.triggerCallback('BeforeInit', _this);

      // Preserve data
      _this.destroy(true);

      // Disable on mobile browsers
      if ( _this.options.disableOnMobile && _this.utils.isMobile() ) {
        _this.disableOnMobile = true;
        return;
      }

      // Get classes
      _this.classes = _this.getClassNames();

      // Create elements
      var input              = $('<input/>', { 'class': _this.classes.input, 'readonly': _this.utils.isMobile() });
      var items              = $('<div/>',   { 'class': _this.classes.items, 'tabindex': -1 });
      var itemsScroll        = $('<div/>',   { 'class': _this.classes.scroll });
      var wrapper            = $('<div/>',   { 'class': _this.classes.prefix, 'html': _this.options.arrowButtonMarkup });
      var label              = $('<span/>',  { 'class': 'label' });
      var outerWrapper       = _this.$element.wrap('<div/>').parent().append(wrapper.prepend(label), items, input);
      var hideSelectWrapper  = $('<div/>',   { 'class': _this.classes.hideselect });

      _this.elements = {
        input        : input,
        items        : items,
        itemsScroll  : itemsScroll,
        wrapper      : wrapper,
        label        : label,
        outerWrapper : outerWrapper
      };

      if ( _this.options.nativeOnMobile && _this.utils.isMobile() ) {
        _this.elements.input = undefined;
        hideSelectWrapper.addClass(_this.classes.prefix + '-is-native');

        _this.$element.on('change', function() {
          _this.refresh();
        });
      }

      _this.$element
        .on(_this.eventTriggers)
        .wrap(hideSelectWrapper);

      _this.originalTabindex = _this.$element.prop('tabindex');
      _this.$element.prop('tabindex', -1);

      _this.populate();
      _this.activate();

      _this.utils.triggerCallback('Init', _this);
    },

    /** Activates the plugin */
    activate: function() {
      var _this = this;
      var hiddenChildren = _this.elements.items.closest(':visible').children(':hidden').addClass(_this.classes.tempshow);
      var originalWidth = _this.$element.width();

      hiddenChildren.removeClass(_this.classes.tempshow);

      _this.utils.triggerCallback('BeforeActivate', _this);

      _this.elements.outerWrapper.prop('class',
        _this.utils.arrayToClassname([
          _this.classes.wrapper,
          _this.$element.prop('class').replace(/\S+/g, _this.classes.prefix + '-$&'),
          _this.options.responsive ? _this.classes.responsive : ''
        ])
      );

      if ( _this.options.inheritOriginalWidth && originalWidth > 0 ) {
        _this.elements.outerWrapper.width(originalWidth);
      }

      _this.unbindEvents();

      if ( !_this.$element.prop('disabled') ) {
        _this.state.enabled = true;

        // Not disabled, so... Removing disabled class
        _this.elements.outerWrapper.removeClass(_this.classes.disabled);

        // Remove styles from items box
        // Fix incorrect height when refreshed is triggered with fewer options
        _this.$li = _this.elements.items.removeAttr('style').find('li');

        _this.bindEvents();
      } else {
        _this.elements.outerWrapper.addClass(_this.classes.disabled);

        if ( _this.elements.input ) {
          _this.elements.input.prop('disabled', true);
        }
      }

      _this.utils.triggerCallback('Activate', _this);
    },

    /**
     * Generate classNames for elements
     *
     * @return {object} Classes object
     */
    getClassNames: function() {
      var _this = this;
      var customClass = _this.options.customClass;
      var classesObj = {};

      $.each(classList.split(' '), function(i, currClass) {
        var c = customClass.prefix + currClass;
        classesObj[currClass.toLowerCase()] = customClass.camelCase ? c : _this.utils.toDash(c);
      });

      classesObj.prefix = customClass.prefix;

      return classesObj;
    },

    /** Set the label text */
    setLabel: function() {
      var _this = this;
      var labelBuilder = _this.options.labelBuilder;

      if ( _this.state.multiple ) {
        // Make sure currentValues is an array
        var currentValues = $.isArray(_this.state.currValue) ? _this.state.currValue : [_this.state.currValue];
        // I'm not happy with this, but currentValues can be an empty
        // array and we need to fallback to the default option.
        currentValues = currentValues.length === 0 ? [0] : currentValues;

        var labelMarkup = $.map(currentValues, function(value) {
          return $.grep(_this.lookupItems, function(item) {
            return item.index === value;
          })[0]; // we don't want nested arrays here
        });

        labelMarkup = $.grep(labelMarkup, function(item) {
          // Hide default (please choose) if more then one element were selected.
          // If no option value were given value is set to option text by default
          if ( labelMarkup.length > 1 || labelMarkup.length === 0 ) {
            return $.trim(item.value) !== '';
          }
          return item;
        });

        labelMarkup = $.map(labelMarkup, function(item) {
          return $.isFunction(labelBuilder)
            ? labelBuilder(item)
            : _this.utils.format(labelBuilder, item);
        });

        // Limit the amount of selected values shown in label
        if ( _this.options.multiple.maxLabelEntries ) {
          if ( labelMarkup.length >= _this.options.multiple.maxLabelEntries + 1 ) {
            labelMarkup = labelMarkup.slice(0, _this.options.multiple.maxLabelEntries);
            labelMarkup.push(
              $.isFunction(labelBuilder)
                ? labelBuilder({ text: '...' })
                : _this.utils.format(labelBuilder, { text: '...' }));
          } else {
            labelMarkup.slice(labelMarkup.length - 1);
          }
        }
        _this.elements.label.html(labelMarkup.join(_this.options.multiple.separator));

      } else {
        var currItem = _this.lookupItems[_this.state.currValue];

        _this.elements.label.html(
          $.isFunction(labelBuilder)
            ? labelBuilder(currItem)
            : _this.utils.format(labelBuilder, currItem)
        );
      }
    },

    /** Get and save the available options */
    populate: function() {
      var _this = this;
      var $options = _this.$element.children();
      var $justOptions = _this.$element.find('option');
      var $selected = $justOptions.filter(':selected');
      var selectedIndex = $justOptions.index($selected);
      var currIndex = 0;
      var emptyValue = (_this.state.multiple ? [] : 0);

      if ( $selected.length > 1 && _this.state.multiple ) {
        selectedIndex = [];
        $selected.each(function() {
          selectedIndex.push($(this).index());
        });
      }

      _this.state.currValue = (~selectedIndex ? selectedIndex : emptyValue);
      _this.state.selectedIdx = _this.state.currValue;
      _this.state.highlightedIdx = _this.state.currValue;
      _this.items = [];
      _this.lookupItems = [];

      if ( $options.length ) {
        // Build options markup
        $options.each(function(i) {
          var $elm = $(this);

          if ( $elm.is('optgroup') ) {

            var optionsGroup = {
              element       : $elm,
              label         : $elm.prop('label'),
              groupDisabled : $elm.prop('disabled'),
              items         : []
            };

            $elm.children().each(function(i) {
              var $elm = $(this);

              optionsGroup.items[i] = _this.getItemData(currIndex, $elm, optionsGroup.groupDisabled || $elm.prop('disabled'));

              _this.lookupItems[currIndex] = optionsGroup.items[i];

              currIndex++;
            });

            _this.items[i] = optionsGroup;

          } else {

            _this.items[i] = _this.getItemData(currIndex, $elm, $elm.prop('disabled'));

            _this.lookupItems[currIndex] = _this.items[i];

            currIndex++;

          }
        });

        _this.setLabel();
        _this.elements.items.append( _this.elements.itemsScroll.html( _this.getItemsMarkup(_this.items) ) );
      }
    },

    /**
     * Generate items object data
     * @param  {integer} index      - Current item index
     * @param  {node}    $elm       - Current element node
     * @param  {boolean} isDisabled - Current element disabled state
     * @return {object}               Item object
     */
    getItemData: function(index, $elm, isDisabled) {
      var _this = this;

      return {
        index     : index,
        element   : $elm,
        value     : $elm.val(),
        className : $elm.prop('class'),
        text      : $elm.html(),
        slug      : $.trim(_this.utils.replaceDiacritics($elm.html())),
        alt       : $elm.attr('data-alt'),
        selected  : $elm.prop('selected'),
        disabled  : isDisabled
      };
    },

    /**
     * Generate options markup
     *
     * @param  {object} items - Object containing all available options
     * @return {string}         HTML for the options box
     */
    getItemsMarkup: function(items) {
      var _this = this;
      var markup = '<ul>';

      if ( $.isFunction(_this.options.listBuilder) && _this.options.listBuilder ) {
        items = _this.options.listBuilder(items);
      }

      $.each(items, function(i, elm) {
        if ( elm.label !== undefined ) {

          markup += _this.utils.format('<ul class="{1}"><li class="{2}">{3}</li>',
            _this.utils.arrayToClassname([
              _this.classes.group,
              elm.groupDisabled ? 'disabled' : '',
              elm.element.prop('class')
            ]),
            _this.classes.grouplabel,
            elm.element.prop('label')
          );

          $.each(elm.items, function(i, elm) {
            markup += _this.getItemMarkup(elm.index, elm);
          });

          markup += '</ul>';

        } else {

          markup += _this.getItemMarkup(elm.index, elm);

        }
      });

      return markup + '</ul>';
    },

    /**
     * Generate every option markup
     *
     * @param  {number} index    - Index of current item
     * @param  {object} itemData - Current item
     * @return {string}            HTML for the option
     */
    getItemMarkup: function(index, itemData) {
      var _this = this;
      var itemBuilder = _this.options.optionsItemBuilder;
      // limit access to item data to provide a simple interface
      // to most relevant options.
      var filteredItemData = {
        value: itemData.value,
        text : itemData.text,
        slug : itemData.slug,
        index: itemData.index
      };

      return _this.utils.format('<li data-index="{1}" class="{2}">{3}</li>',
        index,
        _this.utils.arrayToClassname([
          itemData.className,
          index === _this.items.length - 1  ? 'last'     : '',
          itemData.disabled                 ? 'disabled' : '',
          itemData.selected                 ? 'selected' : ''
        ]),
        $.isFunction(itemBuilder)
          ? _this.utils.format(itemBuilder(itemData, this.$element, index), itemData)
          : _this.utils.format(itemBuilder, filteredItemData)
      );
    },

    /** Remove events on the elements */
    unbindEvents: function() {
      var _this = this;

      _this.elements.wrapper
        .add(_this.$element)
        .add(_this.elements.outerWrapper)
        .add(_this.elements.input)
        .off(eventNamespaceSuffix);
    },

    /** Bind events on the elements */
    bindEvents: function() {
      var _this = this;

      _this.elements.outerWrapper.on('mouseenter' + eventNamespaceSuffix + ' mouseleave' + eventNamespaceSuffix, function(e) {
        $(this).toggleClass(_this.classes.hover, e.type === 'mouseenter');

        // Delay close effect when openOnHover is true
        if ( _this.options.openOnHover ) {
          clearTimeout(_this.closeTimer);

          if ( e.type === 'mouseleave' ) {
            _this.closeTimer = setTimeout($.proxy(_this.close, _this), _this.options.hoverIntentTimeout);
          } else {
            _this.open();
          }
        }
      });

      // Toggle open/close
      _this.elements.wrapper.on('click' + eventNamespaceSuffix, function(e) {
        _this.state.opened ? _this.close() : _this.open(e);
      });

      // Translate original element focus event to dummy input.
      // Disabled on mobile devices because the default option list isn't
      // shown due the fact that hidden input gets focused
      if ( !(_this.options.nativeOnMobile && _this.utils.isMobile()) ) {
        _this.$element.on('focus' + eventNamespaceSuffix, function() {
          _this.elements.input.focus();
        });

        _this.elements.input
          .prop({ tabindex: _this.originalTabindex, disabled: false })
          .on('keydown' + eventNamespaceSuffix, $.proxy(_this.handleKeys, _this))
          .on('focusin' + eventNamespaceSuffix, function(e) {
            _this.elements.outerWrapper.addClass(_this.classes.focus);

            // Prevent the flicker when focusing out and back again in the browser window
            _this.elements.input.one('blur', function() {
              _this.elements.input.blur();
            });

            if ( _this.options.openOnFocus && !_this.state.opened ) {
              _this.open(e);
            }
          })
          .on('focusout' + eventNamespaceSuffix, function() {
            _this.elements.outerWrapper.removeClass(_this.classes.focus);
          })
          .on('input propertychange', function() {
            var val = _this.elements.input.val();
            var searchRegExp = new RegExp('^' + _this.utils.escapeRegExp(val), 'i');

            // Clear search
            clearTimeout(_this.resetStr);
            _this.resetStr = setTimeout(function() {
              _this.elements.input.val('');
            }, _this.options.keySearchTimeout);

            if ( val.length ) {
              // Search in select options
              $.each(_this.items, function(i, elm) {
                if (elm.disabled) {
                  return;
                }
                if (searchRegExp.test(elm.text) || searchRegExp.test(elm.slug)) {
                  _this.highlight(i);
                  return;
                }
                if (!elm.alt) {
                  return;
                }
                var altItems = elm.alt.split('|');
                for (var ai = 0; ai < altItems.length; ai++) {
                  if (!altItems[ai]) {
                    break;
                  }
                  if (searchRegExp.test(altItems[ai].trim())) {
                    _this.highlight(i);
                    return;
                  }
                }
              });
            }
          });
      }

      _this.$li.on({
        // Prevent <input> blur on Chrome
        mousedown: function(e) {
          e.preventDefault();
          e.stopPropagation();
        },
        click: function() {
          _this.select($(this).data('index'));

          // Chrome doesn't close options box if select is wrapped with a label
          // We need to 'return false' to avoid that
          return false;
        }
      });
    },

    /**
     * Behavior when keyboard keys is pressed
     *
     * @param {object} e - Event object
     */
    handleKeys: function(e) {
      var _this = this;
      var key = e.which;
      var keys = _this.options.keys;

      var isPrevKey = $.inArray(key, keys.previous) > -1;
      var isNextKey = $.inArray(key, keys.next) > -1;
      var isSelectKey = $.inArray(key, keys.select) > -1;
      var isOpenKey = $.inArray(key, keys.open) > -1;
      var idx = _this.state.highlightedIdx;
      var isFirstOrLastItem = (isPrevKey && idx === 0) || (isNextKey && (idx + 1) === _this.items.length);
      var goToItem = 0;

      // Enter / Space
      if ( key === 13 || key === 32 ) {
        e.preventDefault();
      }

      // If it's a directional key
      if ( isPrevKey || isNextKey ) {
        if ( !_this.options.allowWrap && isFirstOrLastItem ) {
          return;
        }

        if ( isPrevKey ) {
          goToItem = _this.utils.previousEnabledItem(_this.lookupItems, idx);
        }

        if ( isNextKey ) {
          goToItem = _this.utils.nextEnabledItem(_this.lookupItems, idx);
        }

        _this.highlight(goToItem);
      }

      // Tab / Enter / ESC
      if ( isSelectKey && _this.state.opened ) {
        _this.select(idx);

        if ( !_this.state.multiple || !_this.options.multiple.keepMenuOpen ) {
          _this.close();
        }

        return;
      }

      // Space / Enter / Left / Up / Right / Down
      if ( isOpenKey && !_this.state.opened ) {
        _this.open();
      }
    },

    /** Update the items object */
    refresh: function() {
      var _this = this;

      _this.populate();
      _this.activate();
      _this.utils.triggerCallback('Refresh', _this);
    },

    /** Set options box width/height */
    setOptionsDimensions: function() {
      var _this = this;

      // Calculate options box height
      // Set a temporary class on the hidden parent of the element
      var hiddenChildren = _this.elements.items.closest(':visible').children(':hidden').addClass(_this.classes.tempshow);
      var maxHeight = _this.options.maxHeight;
      var itemsWidth = _this.elements.items.outerWidth();
      var wrapperWidth = _this.elements.wrapper.outerWidth() - (itemsWidth - _this.elements.items.width());

      // Set the dimensions, minimum is wrapper width, expand for long items if option is true
      if ( !_this.options.expandToItemText || wrapperWidth > itemsWidth ) {
        _this.finalWidth = wrapperWidth;
      } else {
        // Make sure the scrollbar width is included
        _this.elements.items.css('overflow', 'scroll');

        // Set a really long width for _this.elements.outerWrapper
        _this.elements.outerWrapper.width(9e4);
        _this.finalWidth = _this.elements.items.width();
        // Set scroll bar to auto
        _this.elements.items.css('overflow', '');
        _this.elements.outerWrapper.width('');
      }

      _this.elements.items.width(_this.finalWidth).height() > maxHeight && _this.elements.items.height(maxHeight);

      // Remove the temporary class
      hiddenChildren.removeClass(_this.classes.tempshow);
    },

    /** Detect if the options box is inside the window */
    isInViewport: function() {
      var _this = this;

      if (_this.options.forceRenderAbove === true) {
        _this.elements.outerWrapper.addClass(_this.classes.above);
      } else {
        var scrollTop = $win.scrollTop();
        var winHeight = $win.height();
        var uiPosX = _this.elements.outerWrapper.offset().top;
        var uiHeight = _this.elements.outerWrapper.outerHeight();

        var fitsDown = (uiPosX + uiHeight + _this.itemsHeight) <= (scrollTop + winHeight);
        var fitsAbove = (uiPosX - _this.itemsHeight) > scrollTop;

        // If it does not fit below, only render it
        // above it fit's there.
        // It's acceptable that the user needs to
        // scroll the viewport to see the cut off UI
        var renderAbove = !fitsDown && fitsAbove;

        _this.elements.outerWrapper.toggleClass(_this.classes.above, renderAbove);
      }
    },

    /**
     * Detect if currently selected option is visible and scroll the options box to show it
     *
     * @param {Number|Array} index - Index of the selected items
     */
    detectItemVisibility: function(index) {
      var _this = this;
      var $filteredLi = _this.$li.filter('[data-index]');

      if ( _this.state.multiple ) {
        // If index is an array, we can assume a multiple select and we
        // want to scroll to the uppermost selected item!
        // Math.min.apply(Math, index) returns the lowest entry in an Array.
        index = ($.isArray(index) && index.length === 0) ? 0 : index;
        index = $.isArray(index) ? Math.min.apply(Math, index) : index;
      }

      var liHeight = $filteredLi.eq(index).outerHeight();
      var liTop = $filteredLi[index].offsetTop;
      var itemsScrollTop = _this.elements.itemsScroll.scrollTop();
      var scrollT = liTop + liHeight * 2;

      _this.elements.itemsScroll.scrollTop(
        scrollT > itemsScrollTop + _this.itemsHeight ? scrollT - _this.itemsHeight :
          liTop - liHeight < itemsScrollTop ? liTop - liHeight :
            itemsScrollTop
      );
    },

    /**
     * Open the select options box
     *
     * @param {Event} e - Event
     */
    open: function(e) {
      var _this = this;

      if ( _this.options.nativeOnMobile && _this.utils.isMobile()) {
        return false;
      }

      _this.utils.triggerCallback('BeforeOpen', _this);

      if ( e ) {
        e.preventDefault();
        if (_this.options.stopPropagation) {
          e.stopPropagation();
        }
      }

      if ( _this.state.enabled ) {
        _this.setOptionsDimensions();

        // Find any other opened instances of select and close it
        $('.' + _this.classes.hideselect, '.' + _this.classes.open).children()[pluginName]('close');

        _this.state.opened = true;
        _this.itemsHeight = _this.elements.items.outerHeight();
        _this.itemsInnerHeight = _this.elements.items.height();

        // Toggle options box visibility
        _this.elements.outerWrapper.addClass(_this.classes.open);

        // Give dummy input focus
        _this.elements.input.val('');
        if ( e && e.type !== 'focusin' ) {
          _this.elements.input.focus();
        }

        // Delayed binds events on Document to make label clicks work
        setTimeout(function() {
          $doc
            .on('click' + eventNamespaceSuffix, $.proxy(_this.close, _this))
            .on('scroll' + eventNamespaceSuffix, $.proxy(_this.isInViewport, _this));
        }, 1);

        _this.isInViewport();

        // Prevent window scroll when using mouse wheel inside items box
        if ( _this.options.preventWindowScroll ) {
          /* istanbul ignore next */
          $doc.on('mousewheel' + eventNamespaceSuffix + ' DOMMouseScroll' + eventNamespaceSuffix, '.' + _this.classes.scroll, function(e) {
            var orgEvent = e.originalEvent;
            var scrollTop = $(this).scrollTop();
            var deltaY = 0;

            if ( 'detail'      in orgEvent ) { deltaY = orgEvent.detail * -1; }
            if ( 'wheelDelta'  in orgEvent ) { deltaY = orgEvent.wheelDelta;  }
            if ( 'wheelDeltaY' in orgEvent ) { deltaY = orgEvent.wheelDeltaY; }
            if ( 'deltaY'      in orgEvent ) { deltaY = orgEvent.deltaY * -1; }

            if ( scrollTop === (this.scrollHeight - _this.itemsInnerHeight) && deltaY < 0 || scrollTop === 0 && deltaY > 0 ) {
              e.preventDefault();
            }
          });
        }

        _this.detectItemVisibility(_this.state.selectedIdx);

        _this.highlight(_this.state.multiple ? -1 : _this.state.selectedIdx);

        _this.utils.triggerCallback('Open', _this);
      }
    },

    /** Close the select options box */
    close: function() {
      var _this = this;

      _this.utils.triggerCallback('BeforeClose', _this);

      // Remove custom events on document
      $doc.off(eventNamespaceSuffix);

      // Remove visible class to hide options box
      _this.elements.outerWrapper.removeClass(_this.classes.open);

      _this.state.opened = false;

      _this.utils.triggerCallback('Close', _this);
    },

    /** Select current option and change the label */
    change: function() {
      var _this = this;

      _this.utils.triggerCallback('BeforeChange', _this);

      if ( _this.state.multiple ) {
        // Reset old selected
        $.each(_this.lookupItems, function(idx) {
          _this.lookupItems[idx].selected = false;
          _this.$element.find('option').prop('selected', false);
        });

        // Set new selected
        $.each(_this.state.selectedIdx, function(idx, value) {
          _this.lookupItems[value].selected = true;
          _this.$element.find('option').eq(value).prop('selected', true);
        });

        _this.state.currValue = _this.state.selectedIdx;

        _this.setLabel();

        _this.utils.triggerCallback('Change', _this);
      } else if ( _this.state.currValue !== _this.state.selectedIdx ) {
        // Apply changed value to original select
        _this.$element
          .prop('selectedIndex', _this.state.currValue = _this.state.selectedIdx)
          .data('value', _this.lookupItems[_this.state.selectedIdx].text);

        // Change label text
        _this.setLabel();

        _this.utils.triggerCallback('Change', _this);
      }
    },

    /**
     * Highlight option
     * @param {number} index - Index of the options that will be highlighted
     */
    highlight: function(index) {
      var _this = this;
      var $filteredLi = _this.$li.filter('[data-index]').removeClass('highlighted');

      _this.utils.triggerCallback('BeforeHighlight', _this);

      // Parameter index is required and should not be a disabled item
      if ( index === undefined || index === -1 || _this.lookupItems[index].disabled ) {
        return;
      }

      $filteredLi
        .eq(_this.state.highlightedIdx = index)
        .addClass('highlighted');

      _this.detectItemVisibility(index);

      _this.utils.triggerCallback('Highlight', _this);
    },

    /**
     * Select option
     *
     * @param {number} index - Index of the option that will be selected
     */
    select: function(index) {
      var _this = this;
      var $filteredLi = _this.$li.filter('[data-index]');

      _this.utils.triggerCallback('BeforeSelect', _this, index);

      // Parameter index is required and should not be a disabled item
      if ( index === undefined || index === -1 || _this.lookupItems[index].disabled ) {
        return;
      }

      if ( _this.state.multiple ) {
        // Make sure selectedIdx is an array
        _this.state.selectedIdx = $.isArray(_this.state.selectedIdx) ? _this.state.selectedIdx : [_this.state.selectedIdx];

        var hasSelectedIndex = $.inArray(index, _this.state.selectedIdx);
        if ( hasSelectedIndex !== -1 ) {
          _this.state.selectedIdx.splice(hasSelectedIndex, 1);
        } else {
          _this.state.selectedIdx.push(index);
        }

        $filteredLi
          .removeClass('selected')
          .filter(function(index) {
            return $.inArray(index, _this.state.selectedIdx) !== -1;
          })
          .addClass('selected');
      } else {
        $filteredLi
          .removeClass('selected')
          .eq(_this.state.selectedIdx = index)
          .addClass('selected');
      }

      if ( !_this.state.multiple || !_this.options.multiple.keepMenuOpen ) {
        _this.close();
      }

      _this.change();

      _this.utils.triggerCallback('Select', _this, index);
    },

    /**
     * Unbind and remove
     *
     * @param {boolean} preserveData - Check if the data on the element should be removed too
     */
    destroy: function(preserveData) {
      var _this = this;

      if ( _this.state && _this.state.enabled ) {
        _this.elements.items.add(_this.elements.wrapper).add(_this.elements.input).remove();

        if ( !preserveData ) {
          _this.$element.removeData(pluginName).removeData('value');
        }

        _this.$element.prop('tabindex', _this.originalTabindex).off(eventNamespaceSuffix).off(_this.eventTriggers).unwrap().unwrap();

        _this.state.enabled = false;
      }
    }
  };

  // A really lightweight plugin wrapper around the constructor,
  // preventing against multiple instantiations
  $.fn[pluginName] = function(args) {
    return this.each(function() {
      var data = $.data(this, pluginName);

      if ( data && !data.disableOnMobile ) {
        (typeof args === 'string' && data[args]) ? data[args]() : data.init(args);
      } else {
        $.data(this, pluginName, new Selectric(this, args));
      }
    });
  };

  /**
   * Default plugin options
   *
   * @type {object}
   */
  $.fn[pluginName].defaults = {
    onChange             : function(elm) { $(elm).change(); },
    maxHeight            : 300,
    keySearchTimeout     : 500,
    arrowButtonMarkup    : '<b class="button">&#x25be;</b>',
    disableOnMobile      : false,
    nativeOnMobile       : true,
    openOnFocus          : true,
    openOnHover          : false,
    hoverIntentTimeout   : 500,
    expandToItemText     : false,
    responsive           : false,
    preventWindowScroll  : true,
    inheritOriginalWidth : false,
    allowWrap            : true,
    forceRenderAbove     : false,
    stopPropagation      : true,
    optionsItemBuilder   : '{text}', // function(itemData, element, index)
    labelBuilder         : '{text}', // function(currItem)
    listBuilder          : false,    // function(items)
    keys                 : {
      previous : [37, 38],                 // Left / Up
      next     : [39, 40],                 // Right / Down
      select   : [9, 13, 27],              // Tab / Enter / Escape
      open     : [13, 32, 37, 38, 39, 40], // Enter / Space / Left / Up / Right / Down
      close    : [9, 27]                   // Tab / Escape
    },
    customClass          : {
      prefix: pluginName,
      camelCase: false
    },
    multiple              : {
      separator: ', ',
      keepMenuOpen: true,
      maxLabelEntries: false
    }
  };
}));
/**
 * jquery.mask.js
 * @version: v1.14.11
 * @author: Igor Escobar
 *
 * Created by Igor Escobar on 2012-03-10. Please report any bug at http://blog.igorescobar.com
 *
 * Copyright (c) 2012 Igor Escobar http://blog.igorescobar.com
 *
 * The MIT License (http://www.opensource.org/licenses/mit-license.php)
 *
 * Permission is hereby granted, free of charge, to any person
 * obtaining a copy of this software and associated documentation
 * files (the "Software"), to deal in the Software without
 * restriction, including without limitation the rights to use,
 * copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following
 * conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 * OTHER DEALINGS IN THE SOFTWARE.
 */

/* jshint laxbreak: true */
/* jshint maxcomplexity:17 */
/* global define */


'use strict';

// UMD (Universal Module Definition) patterns for JavaScript modules that work everywhere.
// https://github.com/umdjs/umd/blob/master/jqueryPluginCommonjs.js
(function (factory, jQuery, Zepto) {

    if (typeof define === 'function' && define.amd) {
        define(['jquery'], factory);
    } else if (typeof exports === 'object') {
        module.exports = factory(require('jquery'));
    } else {
        factory(jQuery || Zepto);
    }

}(function ($) {

    var Mask = function (el, mask, options) {

        var p = {
            invalid: [],
            getCaret: function () {
                try {
                    var sel,
                        pos = 0,
                        ctrl = el.get(0),
                        dSel = document.selection,
                        cSelStart = ctrl.selectionStart;

                    // IE Support
                    if (dSel && navigator.appVersion.indexOf('MSIE 10') === -1) {
                        sel = dSel.createRange();
                        sel.moveStart('character', -p.val().length);
                        pos = sel.text.length;
                    }
                    // Firefox support
                    else if (cSelStart || cSelStart === '0') {
                        pos = cSelStart;
                    }

                    return pos;
                } catch (e) {}
            },
            setCaret: function(pos) {
                try {
                    if (el.is(':focus')) {
                        var range, ctrl = el.get(0);

                        // Firefox, WebKit, etc..
                        if (ctrl.setSelectionRange) {
                            ctrl.setSelectionRange(pos, pos);
                        } else { // IE
                            range = ctrl.createTextRange();
                            range.collapse(true);
                            range.moveEnd('character', pos);
                            range.moveStart('character', pos);
                            range.select();
                        }
                    }
                } catch (e) {}
            },
            events: function() {
                el
                .on('keydown.mask', function(e) {
                    el.data('mask-keycode', e.keyCode || e.which);
                    el.data('mask-previus-value', el.val());
                    el.data('mask-previus-caret-pos', p.getCaret());
                    p.maskDigitPosMapOld = p.maskDigitPosMap;
                })
                .on($.jMaskGlobals.useInput ? 'input.mask' : 'keyup.mask', p.behaviour)
                .on('paste.mask drop.mask', function() {
                    setTimeout(function() {
                        el.keydown().keyup();
                    }, 100);
                })
                .on('change.mask', function(){
                    el.data('changed', true);
                })
                .on('blur.mask', function(){
                    if (oldValue !== p.val() && !el.data('changed')) {
                        el.trigger('change');
                    }
                    el.data('changed', false);
                })
                // it's very important that this callback remains in this position
                // otherwhise oldValue it's going to work buggy
                .on('blur.mask', function() {
                    oldValue = p.val();
                })
                // select all text on focus
                .on('focus.mask', function (e) {
                    if (options.selectOnFocus === true) {
                        $(e.target).select();
                    }
                    // This focus was killing our own focus binding, so have to replicate that code here.
                    $('#billing-info').find('label').removeClass('active');
                    $(this).closest('tr').find('label:not(#address_2_spaceholder)').addClass('active');
                })
                // clear the value if it not complete the mask
                .on('focusout.mask', function() {
                    if (options.clearIfNotMatch && !regexMask.test(p.val())) {
                       p.val('');
                   }
                });
            },
            getRegexMask: function() {
                var maskChunks = [], translation, pattern, optional, recursive, oRecursive, r;

                for (var i = 0; i < mask.length; i++) {
                    translation = jMask.translation[mask.charAt(i)];

                    if (translation) {

                        pattern = translation.pattern.toString().replace(/.{1}$|^.{1}/g, '');
                        optional = translation.optional;
                        recursive = translation.recursive;

                        if (recursive) {
                            maskChunks.push(mask.charAt(i));
                            oRecursive = {digit: mask.charAt(i), pattern: pattern};
                        } else {
                            maskChunks.push(!optional && !recursive ? pattern : (pattern + '?'));
                        }

                    } else {
                        maskChunks.push(mask.charAt(i).replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&'));
                    }
                }

                r = maskChunks.join('');

                if (oRecursive) {
                    r = r.replace(new RegExp('(' + oRecursive.digit + '(.*' + oRecursive.digit + ')?)'), '($1)?')
                         .replace(new RegExp(oRecursive.digit, 'g'), oRecursive.pattern);
                }

                return new RegExp(r);
            },
            destroyEvents: function() {
                // Modified - this was incorrectly destroying all events.
                var events = ['input', 'keydown', 'keyup', 'paste', 'drop', 'blur', 'focusout', ''];
                for(var i = 0; i < events.length; i++){
                    el.off(events[i] = '.mask');
                }
            },
            val: function(v) {
                var isInput = el.is('input'),
                    method = isInput ? 'val' : 'text',
                    r;

                if (arguments.length > 0) {
                    if (el[method]() !== v) {
                        el[method](v);
                    }
                    r = el;
                } else {
                    r = el[method]();
                }

                return r;
            },
            calculateCaretPosition: function() {
                var oldVal = el.data('mask-previus-value') || '',
                    newVal = p.getMasked(),
                    caretPosNew = p.getCaret();
                if (oldVal !== newVal) {
                    var caretPosOld = el.data('mask-previus-caret-pos') || 0,
                        newValL = newVal.length,
                        oldValL = oldVal.length,
                        maskDigitsBeforeCaret = 0,
                        maskDigitsAfterCaret = 0,
                        maskDigitsBeforeCaretAll = 0,
                        maskDigitsBeforeCaretAllOld = 0,
                        i = 0;

                    for (i = caretPosNew; i < newValL; i++) {
                        if (!p.maskDigitPosMap[i]) {
                            break;
                        }
                        maskDigitsAfterCaret++;
                    }

                    for (i = caretPosNew - 1; i >= 0; i--) {
                        if (!p.maskDigitPosMap[i]) {
                            break;
                        }
                        maskDigitsBeforeCaret++;
                    }

                    for (i = caretPosNew - 1; i >= 0; i--) {
                        if (p.maskDigitPosMap[i]) {
                            maskDigitsBeforeCaretAll++;
                        }
                    }

                    for (i = caretPosOld - 1; i >= 0; i--) {
                        if (p.maskDigitPosMapOld[i]) {
                            maskDigitsBeforeCaretAllOld++;
                        }
                    }

                    if (caretPosNew > oldValL) {
                      // if the cursor is at the end keep it there
                      caretPosNew = newValL;
                    }
                    else if (caretPosOld >= caretPosNew && caretPosOld !== oldValL) {
                        if (!p.maskDigitPosMapOld[caretPosNew])  {
                          var caretPos = caretPosNew;
                          caretPosNew -= maskDigitsBeforeCaretAllOld - maskDigitsBeforeCaretAll;
                          caretPosNew -= maskDigitsBeforeCaret;
                          if (p.maskDigitPosMap[caretPosNew])  {
                            caretPosNew = caretPos;
                          }
                        }
                    }
                    else if (caretPosNew > caretPosOld) {
                        caretPosNew += maskDigitsBeforeCaretAll - maskDigitsBeforeCaretAllOld;
                        caretPosNew += maskDigitsAfterCaret;
                    }
                }
                return caretPosNew;
            },
            behaviour: function(e) {
                e = e || window.event;
                p.invalid = [];

                var keyCode = el.data('mask-keycode');

                if ($.inArray(keyCode, jMask.byPassKeys) === -1) {
                    var newVal   = p.getMasked(),
                        caretPos = p.getCaret();

                    setTimeout(function() {
                      p.setCaret(p.calculateCaretPosition());
                    }, 10);

                    p.val(newVal);
                    p.setCaret(caretPos);
                    return p.callbacks(e);
                }
            },
            getMasked: function(skipMaskChars, val) {
                var buf = [],
                    value = val === undefined ? p.val() : val + '',
                    m = 0, maskLen = mask.length,
                    v = 0, valLen = value.length,
                    offset = 1, addMethod = 'push',
                    resetPos = -1,
                    maskDigitCount = 0,
                    maskDigitPosArr = [],
                    lastMaskChar,
                    check;

                if (options.reverse) {
                    addMethod = 'unshift';
                    offset = -1;
                    lastMaskChar = 0;
                    m = maskLen - 1;
                    v = valLen - 1;
                    check = function () {
                        return m > -1 && v > -1;
                    };
                } else {
                    lastMaskChar = maskLen - 1;
                    check = function () {
                        return m < maskLen && v < valLen;
                    };
                }

                var lastUntranslatedMaskChar;
                while (check()) {
                    var maskDigit = mask.charAt(m),
                        valDigit = value.charAt(v),
                        translation = jMask.translation[maskDigit];

                    if (translation) {
                        if (valDigit.match(translation.pattern)) {
                            buf[addMethod](valDigit);
                             if (translation.recursive) {
                                if (resetPos === -1) {
                                    resetPos = m;
                                } else if (m === lastMaskChar) {
                                    m = resetPos - offset;
                                }

                                if (lastMaskChar === resetPos) {
                                    m -= offset;
                                }
                            }
                            m += offset;
                        } else if (valDigit === lastUntranslatedMaskChar) {
                            // matched the last untranslated (raw) mask character that we encountered
                            // likely an insert offset the mask character from the last entry; fall
                            // through and only increment v
                            maskDigitCount--;
                            lastUntranslatedMaskChar = undefined;
                        } else if (translation.optional) {
                            m += offset;
                            v -= offset;
                        } else if (translation.fallback) {
                            buf[addMethod](translation.fallback);
                            m += offset;
                            v -= offset;
                        } else {
                          p.invalid.push({p: v, v: valDigit, e: translation.pattern});
                        }
                        v += offset;
                    } else {
                        if (!skipMaskChars) {
                            buf[addMethod](maskDigit);
                        }

                        if (valDigit === maskDigit) {
                            maskDigitPosArr.push(v);
                            v += offset;
                        } else {
                            lastUntranslatedMaskChar = maskDigit;
                            maskDigitPosArr.push(v + maskDigitCount);
                            maskDigitCount++;
                        }

                        m += offset;
                    }
                }

                var lastMaskCharDigit = mask.charAt(lastMaskChar);
                if (maskLen === valLen + 1 && !jMask.translation[lastMaskCharDigit]) {
                    buf.push(lastMaskCharDigit);
                }

                var newVal = buf.join('');
                p.mapMaskdigitPositions(newVal, maskDigitPosArr, valLen);
                return newVal;
            },
            mapMaskdigitPositions: function(newVal, maskDigitPosArr, valLen) {
              var maskDiff = options.reverse ? newVal.length - valLen : 0;
              p.maskDigitPosMap = {};
              for (var i = 0; i < maskDigitPosArr.length; i++) {
                p.maskDigitPosMap[maskDigitPosArr[i] + maskDiff] = 1;
              }
            },
            callbacks: function (e) {
                var val = p.val(),
                    changed = val !== oldValue,
                    defaultArgs = [val, e, el, options],
                    callback = function(name, criteria, args) {
                        if (typeof options[name] === 'function' && criteria) {
                            options[name].apply(this, args);
                        }
                    };

                callback('onChange', changed === true, defaultArgs);
                callback('onKeyPress', changed === true, defaultArgs);
                callback('onComplete', val.length === mask.length, defaultArgs);
                callback('onInvalid', p.invalid.length > 0, [val, e, el, p.invalid, options]);
            }
        };

        el = $(el);
        var jMask = this, oldValue = p.val(), regexMask;

        mask = typeof mask === 'function' ? mask(p.val(), undefined, el,  options) : mask;

        // public methods
        jMask.mask = mask;
        jMask.options = options;
        jMask.remove = function() {
            var caret = p.getCaret();
            p.destroyEvents();
            p.val(jMask.getCleanVal());
            p.setCaret(caret);
            return el;
        };

        // get value without mask
        jMask.getCleanVal = function() {
           return p.getMasked(true);
        };

        // get masked value without the value being in the input or element
        jMask.getMaskedVal = function(val) {
           return p.getMasked(false, val);
        };

       jMask.init = function(onlyMask) {
            onlyMask = onlyMask || false;
            options = options || {};

            jMask.clearIfNotMatch  = $.jMaskGlobals.clearIfNotMatch;
            jMask.byPassKeys       = $.jMaskGlobals.byPassKeys;
            jMask.translation      = $.extend({}, $.jMaskGlobals.translation, options.translation);

            jMask = $.extend(true, {}, jMask, options);

            regexMask = p.getRegexMask();

            if (onlyMask) {
                p.events();
                p.val(p.getMasked());
            } else {
                if (options.placeholder) {
                    el.attr('placeholder' , options.placeholder);
                }

                // this is necessary, otherwise if the user submit the form
                // and then press the "back" button, the autocomplete will erase
                // the data. Works fine on IE9+, FF, Opera, Safari.
                if (el.data('mask')) {
                  el.attr('autocomplete', 'off');
                }

                // detect if is necessary let the user type freely.
                // for is a lot faster than forEach.
                for (var i = 0, maxlength = true; i < mask.length; i++) {
                    var translation = jMask.translation[mask.charAt(i)];
                    if (translation && translation.recursive) {
                        maxlength = false;
                        break;
                    }
                }

                if (maxlength) {
                    el.attr('maxlength', mask.length);
                }

                p.destroyEvents();
                p.events();

                var caret = p.getCaret();
                p.val(p.getMasked());
                p.setCaret(caret);
            }
        };

        jMask.init(!el.is('input'));
    };

    $.maskWatchers = {};
    var HTMLAttributes = function () {
        var input = $(this),
            options = {},
            prefix = 'data-mask-',
            mask = input.attr('data-mask');

        if (input.attr(prefix + 'reverse')) {
            options.reverse = true;
        }

        if (input.attr(prefix + 'clearifnotmatch')) {
            options.clearIfNotMatch = true;
        }

        if (input.attr(prefix + 'selectonfocus') === 'true') {
           options.selectOnFocus = true;
        }

        if (notSameMaskObject(input, mask, options)) {
            return input.data('mask', new Mask(this, mask, options));
        }
    },
    notSameMaskObject = function(field, mask, options) {
        options = options || {};
        var maskObject = $(field).data('mask'),
            stringify = JSON.stringify,
            value = $(field).val() || $(field).text();
        try {
            if (typeof mask === 'function') {
                mask = mask(value);
            }
            return typeof maskObject !== 'object' || stringify(maskObject.options) !== stringify(options) || maskObject.mask !== mask;
        } catch (e) {}
    },
    eventSupported = function(eventName) {
        var el = document.createElement('div'), isSupported;

        eventName = 'on' + eventName;
        isSupported = (eventName in el);

        if ( !isSupported ) {
            el.setAttribute(eventName, 'return;');
            isSupported = typeof el[eventName] === 'function';
        }
        el = null;

        return isSupported;
    };

    $.fn.mask = function(mask, options) {
        options = options || {};
        var selector = this.selector,
            globals = $.jMaskGlobals,
            interval = globals.watchInterval,
            watchInputs = options.watchInputs || globals.watchInputs,
            maskFunction = function() {
                if (notSameMaskObject(this, mask, options)) {
                    return $(this).data('mask', new Mask(this, mask, options));
                }
            };

        $(this).each(maskFunction);

        if (selector && selector !== '' && watchInputs) {
            clearInterval($.maskWatchers[selector]);
            $.maskWatchers[selector] = setInterval(function(){
                $(document).find(selector).each(maskFunction);
            }, interval);
        }
        return this;
    };

    $.fn.masked = function(val) {
        return this.data('mask').getMaskedVal(val);
    };

    $.fn.unmask = function() {
        clearInterval($.maskWatchers[this.selector]);
        delete $.maskWatchers[this.selector];
        return this.each(function() {
            var dataMask = $(this).data('mask');
            if (dataMask) {
                dataMask.remove().removeData('mask');
            }
        });
    };

    $.fn.cleanVal = function() {
        return this.data('mask').getCleanVal();
    };

    $.applyDataMask = function(selector) {
        selector = selector || $.jMaskGlobals.maskElements;
        var $selector = (selector instanceof $) ? selector : $(selector);
        $selector.filter($.jMaskGlobals.dataMaskAttr).each(HTMLAttributes);
    };

    var globals = {
        maskElements: 'input,td,span,div',
        dataMaskAttr: '*[data-mask]',
        dataMask: true,
        watchInterval: 300,
        watchInputs: true,
        // old versions of chrome dont work great with input event
        useInput: !/Chrome\/[2-4][0-9]|SamsungBrowser/.test(window.navigator.userAgent) && eventSupported('input'),
        watchDataMask: false,
        byPassKeys: [9, 16, 17, 18, 36, 37, 38, 39, 40, 91],
        translation: {
            '0': {pattern: /\d/},
            '9': {pattern: /\d/, optional: true},
            '#': {pattern: /\d/, recursive: true},
            'A': {pattern: /[a-zA-Z0-9]/},
            'S': {pattern: /[a-zA-Z]/}
        }
    };

    $.jMaskGlobals = $.jMaskGlobals || {};
    globals = $.jMaskGlobals = $.extend(true, {}, globals, $.jMaskGlobals);

    // looking for inputs with data-mask attribute
    if (globals.dataMask) {
        $.applyDataMask();
    }

    setInterval(function() {
        if ($.jMaskGlobals.watchDataMask) {
            $.applyDataMask();
        }
    }, globals.watchInterval);
}, window.jQuery, window.Zepto));
(function() {
  var get_analytics_from_shop_item, root;

  String.prototype.titleize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
  };

  get_analytics_from_shop_item = function(mo) {
    mo['Product Color'] = $('p.style').text();
    mo['Product Cost'] = $('p.price').text().replace(/[^\d\.]/, '');
    mo['Currency'] = $('p.price span').data('currency');
    mo['Product Name'] = $('#details h1').text();
    mo['Category'] = $('#details h1').data('category');
    mo['Sold Out?'] = $('.button.sold-out').length > 0;
    mo['Product Number'] = $('#details h1').data('ino');
    mo['Release Week'] = $('#details h1').data('rw');
    mo['Release Date'] = $('#details h1').data('rd');
    return mo;
  };

  root = typeof exports !== "undefined" && exports !== null ? exports : this;

  root.ga_track = function() {
    var action, args, event_name, ga_action, mo, mp_only;
    args = [].slice.call(arguments);
    action = args.shift();
    if (args[0] === "mp_only") {
      mp_only = true;
      args.shift();
    }
    ga_action = [];
    if (action.match(/ecommerce/)) {
      if (typeof ga !== "undefined" && ga !== null) {
        ga('require', 'ecommerce', 'ecommerce.js');
      }
      if (typeof ga_eu !== "undefined" && ga_eu !== null) {
        ga_eu('require', 'ecommerce', 'ecommerce.js');
      }
      ga_action = [action];
    } else {
      ga_action = ['send', action];
    }
    if ((typeof ga !== "undefined" && ga !== null) && !mp_only) {
      ga.apply(ga, ga_action.concat(args));
    }
    if ((typeof ga_eu !== "undefined" && ga_eu !== null) && !mp_only) {
      ga_eu.apply(ga, ga_action.concat(args));
    }
    if ((typeof mixpanel !== "undefined" && mixpanel !== null)) {
      mo = {
        URL: location.pathname,
        'Page Name': document.title.replace('Supreme: ', ''),
        Season: 'FW17',
        'Device Type': 'Desktop',
        'Event Name': action
      };
      mo['Site Region'] = $('body').hasClass('us') ? 'US' : $('body').hasClass('eu') ? 'EU' : 'JP';
      if (action === 'Add to Cart Attempt') {
        mo = get_analytics_from_shop_item(mo);
        mo['Product Size'] = 'Medium';
        mixpanel.track('Add to Cart Attempt', mo);
      }
      if (action === 'Purchase Attempt') {
        $.each(args[0], function(index, val) {
          return mixpanel.track('Purchase Attempt', $.extend(mo, val));
        });
      }
      if (action === "Purchase Success" || action === "Checkout View") {
        mixpanel.track(action, $.extend(mo, args[0]));
      }
      if (action === "pageview") {
        if (location.pathname.match(/^\/shop\/?$/) || location.pathname.match(/^\/shop\/all/)) {
          if (location.pathname.match(/shop\/all\/[a-z]/i)) {
            mo['Shop View Type'] = location.pathname.split("/").slice(-1)[0].titleize();
          } else if (location.pathname.match(/shop\/all/i)) {
            mo['Shop View Type'] = "All";
          } else {
            mo['Shop View Type'] = "Tile";
          }
          event_name = 'Shop View';
        } else if (location.pathname.match(/^\/shop/) && location.pathname.split('/').length > 3) {
          event_name = 'Product View';
          mo = get_analytics_from_shop_item(mo);
        } else if (!(location.pathname.match(/^\/preview/) && location.pathname.split('/').length > 3) && !location.pathname.match(/^\/shop/) && !location.pathname.match(/^\/checkout/)) {
          event_name = 'Menu Page View';
        }
        mo['Event Name'] = event_name;
        mixpanel.track(event_name, mo);
      }
    }
    if ((typeof _gaq !== "undefined" && _gaq !== null) && !mp_only) {
      action = action.replace('ecommerce:send', 'trans');
      action = action.replace('ecommerce:', '');
      action = action.replace('addTransaction', 'addTrans');
      if (action.match(/^add/)) {
        action = '_' + action;
      } else {
        action = '_track' + action.titleize();
      }
      return _gaq.push([action].concat(args));
    }
  };

}).call(this);
$(document).ready(function() {
  Cart = Backbone.Model.extend({
    url: '/shop/cart.json',
    defaults: {
      sizes: null, // List of sizes
      order_billing_country: ""
    },
    initialize: function(){
      var sizes = new StyleSizes();
      this.set('sizes', sizes); // Init the sizes collection.      
      var self = this;
      // Load up the instance items from local storage.
      // This handles page reloads, etc.
      // for(var i = 0; i < localStorage.length; i++){
      //   var sizeId = localStorage.key(i);        
      //   if(!storageKeyIsProduct(sizeId)){continue;} // This junk key kept appearing in localStorage.
      //   var revivedSize = self.getSizeFromLocalStorage(sizeId);
      //   this.get('sizes').add(revivedSize);
      // }
      
    },
    // Checks if the given style exists in this cart.
    // Returns true/false.
    hasStyle: function(style){
      var matchingSize = this.get('sizes').find(function(s){
        return s.get('style').get('id') == style.get('id');
      });
      return(!_.isUndefined(matchingSize));
    },
    // Returns true of false if the product exists in this cart.
    hasProduct: function(product){
      var matchingSize = this.get('sizes').find(function(s){
        var styleIds = product.get('styles').map(function(sId){ return sId.get('id')});
        return _.include(styleIds, s.get('style').get('id'));
      });
      return(!_.isUndefined(matchingSize));      
    },
    render: function(){
      // console.log('sizes changed');
    },
    hasItemsPreventingFreeShipping: function(){
      var no_free_shipping = false;
      for(var i = 0; i < localStorage.length; i++){
        var sizeId = localStorage.key(i);        
        if(!storageKeyIsProduct(sizeId)){continue;} // This junk key kept appearing in localStorage.
        if(this.getSizeFromLocalStorage(sizeId).get('no_free_shipping')){
          no_free_shipping = true;
        }
      }
      return no_free_shipping;
    },
    hasItemsPreventingCOD: function() {
      var cod_blocked = false;
      for(var i = 0; i < localStorage.length; i++){
        var sizeId = localStorage.key(i);        
        if(!storageKeyIsProduct(sizeId)){continue;} // This junk key kept appearing in localStorage.
        if(this.getSizeFromLocalStorage(sizeId).get('cod_blocked')){
          cod_blocked = true;
        }
      }
      return cod_blocked;      
    },
    hasItemsPreventingCanada: function() {
      var canada_blocked = false;
      for(var i = 0; i < localStorage.length; i++){
        var sizeId = localStorage.key(i);        
        if(!storageKeyIsProduct(sizeId)){continue;} // This junk key kept appearing in localStorage.
        if(this.getSizeFromLocalStorage(sizeId).get('canada_blocked')){
          canada_blocked = true;
        }
      }
      return canada_blocked;      
    },
    itemTotal: function(){
      var sum = 0;
      for(var i = 0; i < localStorage.length; i++){
        var sizeId = localStorage.key(i);        
        if(!storageKeyIsProduct(sizeId)){continue;} // This junk key kept appearing in localStorage.
        var size = this.getSizeFromLocalStorage(sizeId);
        sum = sum + size.get('style').get('product').actualPrice(size.get('qty'));
      }
      return sum;
    },
    // Returns whether the given style can be added to the cart.
    canAddStyle:function(style){
      // If the product's can_add_styles is true
      // then there can be multiple styles of the product in the cart.
      // If it's true AND there's a limit count we can have multiples of that style up to a certain point.
      // Otherwise the product can only exist in the cart once, regardless of style.
      var self = this;
      if(style.get('product').get('can_add_styles')){
        if(this.hasStyle(style)){
          return false;
        } else {
          // See if they've reached the limit count, if that's a factor.
          var buyMultipleLimit = style.get('product').get('can_buy_multiple_with_limit');
          if(buyMultipleLimit > 1){
            // count how many they've got of this product in the cart.
            var inCartCount = 0;
            _.each(style.get('product').get('styles').models, function(s){
              if(self.hasStyle(s)){
                inCartCount++;
              }
            });
            return inCartCount < buyMultipleLimit;
          } else {
            return true;  
          }
        }        
        
      } else {
        // Check if the product exists here at all.;
        if(this.hasProduct(style.get('product'))){          
          return false;          
        }
      }      
      return true;      
    },
    getServerContents: function(callback){
      var self = this;
      var url = '/shop/cart_extended.json';
      $.ajax({
        type: 'GET',
        url:url,
        dataType: 'json',
        success: function(response){
          callback(response);
        },
        error: function(){
        }
      });
    },
    changeQty: function(productId, sizeId, qty){
      var self = this;
      var url = "/shop/" + productId + '/update_qty.json'      
      // curl -d 'size=10510' http://127.0.0.1:3000/shop/1399/update_qty.json
      $.ajax({
        type: 'DELETE',
        url:url, 
        data: {size: sizeId, qty: qty},
        dataType: 'json',
        success: function(response){
          localStorage.setItem(sizeId + '_qty', qty);
          self.trigger('itemAdded');             
          self.trigger('doneModifyingCart');
        },
        error: function(){
          self.trigger('doneModifyingCart');          
        }
      });       
    },
    removeSize: function(productId, sizeId) {
      var self = this;
      var url = "/shop/" + productId + '/remove.json'
      // curl -d 'size=10510' http://127.0.0.1:3000/shop/1399/delete.json
      $.ajax({
        type: 'DELETE',
        url:url, 
        data: {size: sizeId},
        dataType: 'json',
        success: function(response){
          // Take the returned list of available sizes and notify them if anything has sold out.
          // No need to complain about the thing we just removed though.
          var sizeToRemove = self.get('sizes').find(function(s){
            return s.get('id') == parseInt(sizeId);
          })

          self.get('sizes').remove(sizeToRemove);          

          self.removeSizeFromLocalStorage(sizeId);
          self.trigger('itemAdded');             
          
          if(Supreme.app.cart.length() == 0){
            clearCookies();
          }
          
          self.trigger('doneModifyingCart');
          
        },
        error: function(){
          self.trigger('doneModifyingCart');          
        }
      });      
    },
    // Removes all sizes from the cart that are associated with the given product.
    removeProduct: function(product, sizeId){
      this.removeSize(product.get('id'), sizeId);
    },
    length: function(){
      
      // Count the items in localstorage, excluding that nutty junk keys.
      var count = 0;
      for(var i = 0; i < localStorage.length; i++){
        var sizeId = localStorage.key(i);        
        if(!storageKeyIsProduct(sizeId)){continue;} // This junk key kept appearing in localStorage.
        count++;
      }
      return count;
    },
    addSize: function(size, qty, shouldNotTriggerEvents){
      var self = this;
      qty = qty || 1; 
      if(!this.canAddStyle(size.get('style'))){
        this.trigger('doubleItemError');
        return false;
      }

      try {
        var self = this;
        this.get('sizes').add(size, qty);
        var url = "/shop/" + size.get('style').get('product').get('id') + '/add.json'


        $.ajax({
          type: 'POST',
          url:url, 
          data: {s: size.get('id'), st: size.get('style').get('id'), qty: qty},
          dataType: 'json',
          success: function(response){      
            // What if this is sold out?
            // Need to un-add it.
            var foundSize = _.find(response, function(item){
              return size.get('id') == item.size_id;
            });
            
            var sold_out;
            
            if(_.isUndefined(foundSize)){
              sold_out = true;              
              // Means it sold out. Remove it from the cart if it got added and mark it as sold out.      
              Supreme.app.cart.removeSizeDirectly(size.get('id'));
              // Need to mark the UI.
              self.trigger('itemSoldOut')
            } else {
              sold_out = false;
              self.addSizeToLocalStorage(size, qty); // Only add to local once actually added.
              self.trigger('itemAdded');              
            }
            
            var currency;
            if (IS_JAPAN)
              currency = 'JPY'
            else if (IS_EU)
              currency = LANG.currency == "eur" ? 'EUR' : 'GBP'
            else
              currency = 'USD'

            var price = formatCurrency(size.get('style').get('product').actualPrice()).replace(/[^\d\.]/,'')

            mixpanelTrack('Add to Cart Attempt', {Category: _currentCategoryPlural, "Product Color": size.get('style').get('name'), "Product Name": size.get('style').get('product').get('name'), "Product Size": size.get('name'), "Product Cost": price, 'Currency': currency, "Device Type": "Mobile", 'Sold Out?': sold_out});

            self.trigger('doneModifyingCart');            
          },
          error: function(){
            self.trigger('doneModifyingCart');            
          }
        });        
        

      } catch(err) { 
        // Catches dupe sizes. Shouldn't really get here, given the above checks regarding can_add_styles.
        this.trigger('doubleItemError');
        this.trigger('doneModifyingCart');        
      }
    },
    // Returns a real StyleSize object from the JSON string version in local storage,
    // based on the given size ID.
    // Contains the size's style (but that style does not contain all sizes),
    // and the product for the style (again, that product does not contain all styles).
    getSizeFromLocalStorage: function(sizeId){
      var sizeJSON = JSON.parse(localStorage.getItem(sizeId));
      var style = new ProductStyle(sizeJSON.style);
      var product = new Product(Supreme.getProductOverviewDetailsForId(style.get('product_id'), allCategoriesAndProducts));
      product.set('apparel', sizeJSON.apparel), 
      product.set('handling', sizeJSON.handling),       
      style.set('product', product);
      product.set('can_buy_multiple', sizeJSON.can_buy_multiple);
      product.set('purchasable_qty', sizeJSON.purchasable_qty);
      var size = new StyleSize({
        id: sizeJSON.id,
        name: sizeJSON.name,
        stock_level: sizeJSON.stock_level,
        style: style,
        no_free_shipping: sizeJSON.no_free_shipping,
        cod_blocked: sizeJSON.cod_blocked,
        canada_blocked: sizeJSON.canada_blocked,
        qty: localStorage.getItem(sizeId + "_qty")
      });
      return size;
    },
    // Removes the item locally, doesn't hit the server.
    removeSizeDirectly: function(sizeId){ 
      var sizeToRemove = this.get('sizes').find(function(s){
        return s.get('id') == parseInt(sizeId);
      })
      this.get('sizes').remove(sizeToRemove);      // only need to do this because the cart won't rebuild itself from ocalstorage on update. should do that.
      this.removeSizeFromLocalStorage(sizeId);
      this.trigger('itemAdded');           
    },
    // converts to JSON and stringifies the given size,
    // putting it in local storage keyed ot the size ID.
    addSizeToLocalStorage: function(size, qty){
      localStorage.setItem(size.get('id'), JSON.stringify(size.toDeepJSON()));
      this.getSizeFromLocalStorage(size.get('id'));
      localStorage.setItem(size.get('id')+'_qty', qty);
    },
    removeSizeFromLocalStorage: function(sizeId){
      localStorage.removeItem(sizeId);
      localStorage.removeItem(sizeId+'_qty');
    },
    // Given an array of size IDs returns which of the cart's size objects do not have their IDs present.
    soldOutSizesFromSizeIds: function(sizeIds){
      // Go through the cart's size IDs and check that each are in the cookie string.
      // If not collect them.
      var missingSizes = new StyleSizes();
      this.get('sizes').each(function(size){
        var sizeId = size.get('id');
        if(!_.include(sizeIds, sizeId)){
          missingSizes.add(size);
        }
      });
      return missingSizes;
    },    
    // Takes the cookie string from the server and updated the cart with that content.
    // Cart looks like X.--X.--sizeId,styleId-sizeId,styleId....
    updateFromCookie: function(cookieString){
      this.get('sizes').reset();
      var cookieBits = cookieString.split('--');
      var sizeIdBits = cookieBits[2].split('-');
      var self = this;
      _.each(sizeIdBits, function(sizeIdBits){
        // We only have the size ID, but we do need to attach the style and product info.
        var sizeId = parseInt(sizeIdBits.split(',')[0]);            
        var styleId = parseInt(sizeIdBits.split(',')[1]);
        var style = new ProductStyle({id: styleId});
        
        var size = new StyleSize({
          id: sizeId,
          style: style
        });
        self.get('sizes').add(size); // short cut the full size adding method (addSize()), we just want these here in the raw, no triggers.
      });
    },
    quantityForSize: function(size_id){
      var size = this.get('sizes').find(function(s){
        return s.get('id') == parseInt(size_id);
      })
      if (size)
        return size.get('qty');
    },
    // Given a style returns the size that exists for that style in the cart, if any.
    // Returns false if it doesn't exist.
    // Based on the assumption that only one size per style can ever exist in the cart.
    getSizeForStyle: function(style){
      var matchingSize = this.get('sizes').find(function(s){
        return s.get('style').get('id') == style.get('id');
      });
      if(_.isUndefined(matchingSize)){
        return false;
      } else {
        return matchingSize;
      }
    },
    // Parse the cart json. Going to be an array of sizes, like:
    // [{in_stock: true, product_id: 1406, size_id: 5120, style_id: 5354}, ... ]
    parse: function(json){
      
      // record each of the sold out item style IDs in session storage
      // so we can flag them as sold out in the cart.
      _.each(json, function(p){
        if(!p.in_stock){
          sessionStorage.setItem("out_of_stock_" + p.size_id, 1);
        } else {
          sessionStorage.removeItem("out_of_stock_" + p.size_id);
        }
      });
      
      // Record the sold out items.
      var self = this;
      // If something is out of stock don't show it, just remove it.
      for(var i = 0; i < localStorage.length; i++){
        var sizeId = localStorage.key(i);        
        
        if(!storageKeyIsProduct(sizeId)){continue;} // This junk key kept appearing in localStorage.          

        var x = _.find(json, function(item){
          return item.size_id == sizeId;
        });
        if(_.isUndefined(x)){
          // Is the current item in the cart not in the cart.json?
          // Remove it.
          self.removeSizeDirectly(sizeId);
        }
      }
    },
    otherItemsTotal: function(){
      var otherItems = this.get('sizes').filter(function(s){
        return !s.get('style').get('product').get('apparel')
      });
      return otherItems.reduce(function(m, size){
        return m + size.get('style').get('product').actualPrice();  
      }, 0);
    },
    shippingTotal: function(country, state){
      if (IS_JAPAN)
        if (FREE_SHIPPING && !this.hasItemsPreventingFreeShipping() && this.itemTotal() >= MIN_JP_FREE)
          return 0;
        else
          return SHIPPING_RATE + this.handlingTotal();
      else if(IS_EU){
        var country_name = COUNTRIES[country];
        var shipping_rate = this.shipping_rate_for_country(country);
        
        if(FREE_SHIPPING && !this.hasItemsPreventingFreeShipping()){
          var item_total = this.itemTotal();
          if(country == 'GB' && item_total > MIN_UK_FREE){
            return 0;
          } else if(this.hasVat(country) && item_total > MIN_EU_FREE){
            return 0; 
          } else if(!this.hasVat(country) && item_total > MIN_NON_EU_FREE){
            return 0;
          } else {}
        }
        
        return shipping_rate;
      } else {
        var shippingAmount = 0;
        
        
        if(FREE_SHIPPING && !this.hasItemsPreventingFreeShipping()){
          var item_total = this.itemTotal();
          if (country.toLowerCase() != "canada" && item_total > MIN_US_FREE){
            return 0;
          } else {}
        }        
        
        if(country.toLowerCase() == "canada"){      
          shippingAmount = shippingRates["canada"];
        } else {
          if(_.include(['AK', 'HI', 'GU', 'PR'], state.toUpperCase())){
            shippingAmount = shippingRates["spec"];
          } else {
            shippingAmount = shippingRates["std"];
          }
        }
        return shippingAmount + this.handlingTotal();
      }

    },
    handlingTotal: function(){
      return this.get('sizes').reduce(function(m, size){
        return m + size.get('style').get('product').get('handling');  
      }, 0);      
    },
    // Returns if the selected country is a VAT country.
    hasVat: function(country){
      if(!IS_EU){
        return 0;
      }      
      return !_.contains(NON_VAT_COUNTRIES, country);
    },
    // Returns the current vat discount for this order, if any.
    vatDiscount: function(country, state){
      if(!IS_EU){
        return 0;
      }
      if(this.hasVat(country)){
        return 0; // No discount, this is a VAT country.
      } else {
        var to_20 = 1.2;
        var it = this.itemTotal();
        var item_total_discount = it - (it / to_20);
        var st = this.shippingTotal(country, state);
        var shipping_total_discount = st - (st / to_20);
        return item_total_discount + shipping_total_discount;
      }
    },
    codTotal: function(credit_card_type){
      if (!IS_JAPAN)
        return 0;

      if(credit_card_type != 'cod'){ return 0; }
      
      cod_chargable_total = this.itemTotal() + this.shippingTotal();

      // Given the chargable total see where we git in the COD rate bands:
      var matched_rate = _.detect(COD_RATES, function(rate_pair){

        threshold = rate_pair[0].fractional;
        rate      = rate_pair[1].fractional;

        if(cod_chargable_total <= threshold){
          return rate;
        };

      });

      return matched_rate[1].fractional;

    },
    taxTotal: function(country, state){
      if(state.toUpperCase() == 'NY'){
        var x = ((this.otherItemsTotal() + this.shippingTotal(country, state)) * TAX_RATE) + this.apparelTaxTotal();

        return Math.round(x);
      } else {
        return 0;
      }
    },
    apparelTaxTotal: function(){
      var at = 0;
      var self = this;
      var apparel = this.get('sizes').select(function(size){
        return size.get('style').get('product').get('apparel') && size.get('style').get('product').actualPrice() >= APPAREL_THRESHOLD;
      });      

      if((apparel.length > 0)){
        var total = apparel.reduce(function(m, size){
          return m + size.get('style').get('product').actualPrice();  
        }, 0);
        at += total * APPAREL_TAX_RATE;
      };
      
      
      return at; 
    },

    orderTotal: function(credit_card_type, country, state) {

      var total = this.itemTotal() + this.taxTotal(country, state) + this.shippingTotal(country, state);
      var cod = this.codTotal(credit_card_type);
      if(cod > 0){
        total = parseInt(total) + parseInt(cod);
      }

      if(IS_EU){
        total = total - this.vatDiscount(country);
      }
      return total;
      
    },
    // Given a country code (for EU) return the shipping rate.
    shipping_rate_for_country: function(country_code){
      var country = _.detect(COUNTRIES, function(c){ return c.ups_cc == country_code; });
      
      if(!country){
        return DEFAULT_SHIPPING_RATE;
      }
      
      var rate = ZONES[country.zone];
      return rate;
    }
    
  });
});
$(document).ready(function() {
  Category = Backbone.Model.extend({
    defaults: {
       name: null,
       products: null // This will be a CategoryProducts() collection.
     }
  });
});
$(document).ready(function() {
  CheckoutForm = Backbone.Model.extend({
    defaults: {
      order_billing_name: null,
      order_email: null,
      order_tel: null,
      order_billing_address: null,
      order_billing_city: null,
      order_billing_zip: null,
      same_as_billing_address: null,
      order_billing_state: "",
      order_billing_country: IS_JAPAN ? "JAPAN" : (IS_EU ? "GB" : "USA"),
      credit_card_type: 'visa' // Default to visa.
    },
    // Takes the JSON response from a checkout form submission from the server.
    processFormResponse: function(jsonResponse){
      Supreme.app.cart.lastError = "";
      if(jsonResponse.status == "failed"){
        if(_.isUndefined(jsonResponse.errors)){
          // No errors, but have the AVS error? Show that.
          if(jsonResponse.avs){
            window._gaq.push(['_trackEvent', 'checkout-error', 'avs']);
            this.processErrorFormResponse({avs: true});
          } else { // No errors and nothing specific to AVS? Show the default failed payment error.
            window._gaq.push(['_trackEvent', 'checkout-error', 'charge-failed']);
            this.trigger('chargeFailed', jsonResponse.b);
            logError('jsonResponse.errors undefined in processFormResponse', jsonResponse);
          }
        } else { // Do we have actual error rows? Show them.
          window._gaq.push(['_trackEvent', 'checkout-error', 'checkout validation failed']);
          this.processErrorFormResponse(jsonResponse.errors);
          mixpanelTrack('Purchase Attempt', jsonResponse.mpa);
        }
        return true;
      } else if(jsonResponse.status == "paid") {
        this.processSuccessfulFormResponse(jsonResponse.info);
        mixpanelTrack('Purchase Attempt', jsonResponse.mpa);
        mixpanelTrack('Purchase Success', jsonResponse.mps);
        if (mixpanel)
          mixpanel.register({'Repeat Customer': true});

        return true;        
      } else if(jsonResponse.status == "dup"){
        window._gaq.push(['_trackEvent', 'checkout-error', 'dup']);
        this.processDupFormResponse();        
        return false;      
      } else if(jsonResponse.status == "canada"){
        this.processCanadaFormResponse();        
        return false;
      } else if(jsonResponse.status == "blocked_country"){
        this.processBlockedCountryFormResponse();        
        return false;        
      } else if(jsonResponse.status == "blacklisted"){
        this.processBlackListedFormResponse();        
        return false;              
      } else if(jsonResponse.status == "outOfStock"){
        this.processOutOfStockFormResponse();
        mixpanelTrack('Purchase Attempt', jsonResponse.mpa);
        return false;      
      } else if(jsonResponse.status == 'paypal'){
        window.location.href = jsonResponse.redirect_url;
        // Unless they checked Remember We, we clear the address cookie.
        if(_.isNull(readCookie('remember_me'))){
          eraseCookie('js-address');
        }
      } else {
        // Other reason? Assume the charge failed.
        window._gaq.push(['_trackEvent', 'checkout-error', 'charge-failed-2']);
        this.trigger('chargeFailed');
        logError('else error in processFormResponse', jsonResponse);
      }
    },
    processOutOfStockFormResponse: function(){
      Supreme.app.cart.lastError = "outOfStock";
      this.trigger('outOfStockError');      
    },
    processDupFormResponse: function(){
      Supreme.app.cart.lastError = "dup";
      this.trigger('dupError');
    },
    processCanadaFormResponse: function(){
      Supreme.app.cart.lastError = "canada";
      this.trigger('dupError');
    },
    processBlockedCountryFormResponse: function(){
      Supreme.app.cart.lastError = "blocked_country";
      this.trigger('dupError');
    },
    processBlackListedFormResponse: function(){
      Supreme.app.cart.lastError = "blacklisted";
      this.trigger('dupError');
    },

    processSuccessfulFormResponse: function(orderInfo){
      // All good!
      // Show the confirmation screen.
      clearCookies();

      // Unless they checked Remember We, we clear the address cookie.
      if(_.isNull(readCookie('remember_me'))){
        eraseCookie('js-address');
      }

      var orderConfirmationView = new OrderConfirmationView({
        el: $('#main')[0],
        model: orderInfo    
      });
      orderConfirmationView.render();
      localStorage.clear();
      // Reset the cart.
      $('#cart-link').remove();
      Supreme.app.cart = new Cart();
      eraseCookie('cart');
      Supreme.app.cartLinkView = new CartLinkView({model: Supreme.app.cart});
      $('header').prepend(Supreme.app.cartLinkView.render().el);      
      // Need this on the HTML so we can know to show the mailing list checkbox.
      $('html').addClass('orderConfirm');
    },
    processErrorFormResponse: function(errors){
      // Send the errors back to the form to be rendered.
      this.trigger('checkoutErrors', errors);
    },
    pollCardStatus: function(orderId){
      var self = this;
      $.ajax({
        type: 'POST',
        url: '/check_order_status.json',
        dataType: 'json',
        success: function(body) {
          if(body.status == "failed"){
            self.trigger('chargeFailed');
          }
        },
        error: function(xhr, type) { }
      })      
    }
    
  });
});
$(document).ready(function() {
  LookbookItem = Backbone.Model.extend({
    defaults: {
      caption: null,
      medium: null,
      name: null, // This is used?
      products: null, // Is this used?
      small: null,
      title: null, // Is this used?
      url: null
     },
      // Need to strip <a> tags.     
     stripSomeMarkupFromCaption: function(){
       var caption = this.get('caption').replace(/<a.*?>/ig, '').replace(/<\/a>/ig, '');
       this.set('caption', caption);
     }
  });
});
$(document).ready(function() {
  // Used for product detail pages, loaded remotely.
  Product = Backbone.Model.extend({
    url: function(){
      return "/shop/" + this.get('id') + ".json";
    },
    initialize: function(){
      // Watch the image url so we can set the thumbnail image url when it comes in.
      var self = this;
      this.bind("change:styles", function(){
        var firstStyle = _.first(self.get('styles'));
      });
    },
    defaults: {
      purchasable_qty: 0,
      categoryName: null,
      styles: null, // a collection of styles.
      initialImageUrl: null,
      name: null,
      price: null,
      price_euro: null,
      sale_price: null,
      sale_price_euro: null,
      selectedStyle: null,
      can_add_styles: false,
      can_buy_multiple: false,
      can_buy_multiple_with_limit: 0,
      no_free_shipping: false,
      selectedStyleAlt: 0, // 0 defaults to the standard photo, 1..n refers to alt style images.
      qty: 0
    },
    showAlt: function(altIndex){
      this.set('photoIndex', altIndex);
    },
    actualPrice: function(qty){
      if(_.isUndefined(qty)){ // passing in the quantity is optional.
        qty = 1;
      } else {
        qty = parseInt(qty);
      }
      if(this.get('sale_price') != 0 && SALE_VISIBLE){
        if (LANG.currency == "eur")
          return this.get('sale_price_euro') * qty; 
        return this.get('sale_price') * qty; 
      } else {
        if (LANG.currency == "eur")
          return this.get('price_euro') * qty; 

        return this.get('price') * qty;
      }
    },
    isOnSale: function(){
      return this.get('sale_price') != 0 && SALE_VISIBLE;
     },    
    sizeForId: function(sizeId){
      var size;
      this.get('styles').each(function(style){
        var found = style.get('sizes').find(function(s){        
          return s.get('id') == sizeId;
        });
        if(!_.isUndefined(found)){
          size = found; 
          return;
        }
      });
      return size;
    },
    // Given a batch of product data from the product detail fetch, including style and size info, build the product.
    parse: function(json, xhr){
      // mobile versioning
      var reloading = false;
      if(typeof window.splayver === "undefined") {
        if (xhr.getResponseHeader("X-Splay-Version") != null) {
          if (xhr.getResponseHeader("X-Splay-Version").match(/^[0-9a-f]{16}$/) != null && xhr.getResponseHeader("X-Splay-Version").match(/^[0-9a-f]{16}$/).length == 1) {
            if (xhr.getResponseHeader("X-Splay-Version").match(/^[0-9a-f]{16}$/)[0] == xhr.getResponseHeader("X-Splay-Version")) {
              window.splayver = xhr.getResponseHeader("X-Splay-Version");
            }
          }
        }
      } else {
        if (xhr.getResponseHeader("X-Splay-Version") != null && xhr.getResponseHeader("X-Splay-Version") != window.splayver) {
          if (xhr.getResponseHeader("X-Splay-Version").match(/^[0-9a-f]{16}$/) != null && xhr.getResponseHeader("X-Splay-Version").match(/^[0-9a-f]{16}$/).length == 1) {
            if (xhr.getResponseHeader("X-Splay-Version").match(/^[0-9a-f]{16}$/)[0] == xhr.getResponseHeader("X-Splay-Version")) {
              window.splayver = xhr.getResponseHeader("X-Splay-Version");
              reloading = true;
              location.reload();
            }
          }
        }
      }
      
      if (!reloading) {
        var self = this;
        var ps = new ProductStyles();
        this.set('styles', ps);
        this.set('description', json.description);
        this.set('handling', json.handling);
        this.set('apparel', json.apparel);
        this.set('can_add_styles', json.can_add_styles);
        this.set('can_buy_multiple', json.can_buy_multiple);
        this.set('purchasable_qty', json.purchasable_qty);
        this.set('can_buy_multiple_with_limit', json.can_buy_multiple_with_limit);
        this.set('ino', json.ino);
        this.set('cod_blocked', json.cod_blocked);
        this.set('canada_blocked', json.canada_blocked);


        // Create each new style.
        _.each(json.styles, function(s){
          

          // Swap in our hi res images in the additional images, if needed.
          if(isHiRes()){
            _.each(s.additional, function (addntl, aIndx){
              s.additional[aIndx].image_url       = s.additional[aIndx].image_url_hi;
              s.additional[aIndx].swatch_url      = s.additional[aIndx].swatch_url_hi;
              s.additional[aIndx].zoomed_url      = s.additional[aIndx].zoomed_url_hi;
              s.additional[aIndx].lower_res_zoom  = s.additional[aIndx].image_url; // maintain a reference to the smaller zoom image in case we fall back to it.
            });
          }
        
          var style = new ProductStyle({
            id: s.id, 
            name: s.name, 
            price: s.price,
            description: s.description, 
            swatch_url: (isHiRes() ? s.swatch_url_hi : s.swatch_url),
            zoomed_url: (isHiRes() ? s.mobile_zoomed_url_hi : s.mobile_zoomed_url),
            image_url: (isHiRes() ? s.image_url_hi : s.image_url),
            additional_images: s.additional,
            lower_res_zoom: s.image_url // maintain a reference to the smaller zoom image in case we fall back to it.
          });

          style.set('sizes', new StyleSizes());
          style.set('product', self); // Point to the parent product.
          // Add to that style its sizes.
          _.each(s.sizes, function(sz){
            var size = new StyleSize(sz);
            size.set('no_free_shipping', json.no_free_shipping); // even though this is product level in the DB, we need it on each size when we calc shipping in cart.js.
            size.set('cod_blocked', json.cod_blocked);
            size.set('canada_blocked', json.canada_blocked);
            
            size.set('style', style); // Point to the parent style.
            style.get('sizes').add(size);
          });
          self.get('styles').add(style);
        });
        return {};
      }
    }
  });
});
$(document).ready(function() {
  // Preview product items used in list views.
  ProductPreview = Backbone.Model.extend({
    defaults: {
      id: null,
      name: null,
      price: null,
      sale_price: null,
      image_url: null,
      image_url_hi: null
    }
  });
});
$(document).ready(function() {
  // All products have styles, which include images, size, color, etc.
  ProductStyle = Backbone.Model.extend({
    defaults: {
      name: null,
      id: null,
      image_url: null,
      sizes: null, // A collection of style sizes.
      initialPhotoIndex: 0
    },
    // Returns if this style has no sizes, or all its sizes have 0 stock.
    isSoldOut: function(){
      if(this.get('sizes').length == 0){ return true; }
      if(this.get('sizes').all(function(size){
        return parseInt(size.get('stock_level')) == 0;
      })){ return true };
      return false;
    },
    // Returns the appropriate product photo, taking into account selected alt image if necessary.
    productPhoto: function(){
    // 0 is not alt, how about that.
    // Do we have an initial alt selected? Go with that.
    var idx;
    if(!_.isUndefined(this.get('initialPhotoIndex'))){
      idx = this.get('initialPhotoIndex');
    } else {
       idx = this.get('product').get('selectedStyleAlt');
    }
    
      if(idx > 0){
         return this.get('additional_images')[idx-1].image_url;
      } else {
        return this.get('image_url');
      }
    },
    zoomedPhoto: function(useLowerResImage){

      if(_.isUndefined(useLowerResImage)){
        useLowerResImage = false;
      }

      // 0 is not alt, how about that.
      // Do we have an initial alt selected? Go with that.
      var idx;
      if(!_.isUndefined(this.get('initialPhotoIndex'))){
        idx = this.get('initialPhotoIndex');
      } else {
         idx = this.get('product').get('selectedStyleAlt');
      }

        if(idx > 0){
          if(useLowerResImage){
            console.log('using useLowerResImage');
            return this.get('additional_images')[idx-1].lower_res_zoom;
          } else {
            return this.get('additional_images')[idx-1].zoomed_url;
          }
          
        } else {
          if(useLowerResImage){
            console.log('using useLowerResImage');
            return this.get('lower_res_zoom');
          } else {
            return this.get('zoomed_url');
          }
        }

    }

  });
});
$(document).ready(function() {
  // All styles have a variety of sizes, which contain stock info.
  StyleSize = Backbone.Model.extend({
    defaults: {
      stock_level: null,
      name: null,
      id: null,
      qty: 1 // the quantity the user added to their cart.
    }, 
    // Returns a JSON representation of the size and its style info.
    // This is stuff that we don't have available in the local product/category dump but needs to be
    // carried between products. So it saves some vital stuff required for the cart.
    // The style loses the full product item but gets a product_id.
    // When it's pulled back out and turned into a few objects via getSizeFromLocalStorage()
    // it will match the standard data format.
    toDeepJSON: function(){
      var size = this.toJSON();
      // We won't build a product, so just put some of the product vars on the size, and we'll 
      // work them out when we build the items again.
      size.apparel = this.get('style').get('product').get('apparel');     
      size.handling = this.get('style').get('product').get('handling');
      size.can_buy_multiple = this.get('style').get('product').get('can_buy_multiple');
      size.purchasable_qty = this.get('style').get('product').get('purchasable_qty');
      var style = this.get('style').clone();
      style.set('product_id', this.get('style').get('product').get('id'));      
      style.set('sizes', null); // lose all the sizes on the style.
      style.set('product', null);
      size.style = style.toJSON();
      return size;
    }
  });
});

$(document).ready(function() {
  Categories = Backbone.Collection.extend({
    model: Category,
    // Accepts the giant hash of categories and products and loads up the data.
    populate: function(categoriesAndProducts) {
      var self = this;
      _.each(categoriesAndProducts.products_and_categories, function(products, categoryName){
	
				// Transform our shortened products into full named products.
				var expandedProducts = [];
				_.each(products, function(p){
          
          
          var image_url = (isHiRes() ? p.image_url_hi : p.image_url);

					expandedProducts.push(new Product({
						id: p.id,
						name: p.name,
						image_url: image_url,
						price: p.price,
						sale_price: p.sale_price,
            price_euro: p.price_euro,
            sale_price_euro: p.sale_price_euro,
						new_item: p.new_item,
						position: p.position
					}));
				});

        var categoryProducts = new CategoryProducts(expandedProducts);
        var category = new Category({name: categoryName, products: categoryProducts});
        self.add(category);
      });
    }    
  });  
});
$(document).ready(function() {
  // Used on a category list view.
  CategoryProducts = Backbone.Collection.extend({
    model: ProductPreview
  });
});
$(document).ready(function() {
  Lookbook = Backbone.Collection.extend({
    model: LookbookItem,
    url: '/lookbooks.json',
    parse: function (response) {
      this.title = response.title;
      return response.images;
    }
    
  });
});
    
$(document).ready(function() {
  ProductStyles = Backbone.Collection.extend({
    model: ProductStyle
  })  
});
$(document).ready(function() {
  StyleSizes = Backbone.Collection.extend({
    model: StyleSize
  })
});
$(document).ready(function() {
  AddToCartButtonView = Backbone.View.extend({
    tagName: 'span',
    className: 'cart-button',
    initialize: function(){
      this.render = _.bind(this.render, this);
      this.itemSoldOut = _.bind(this.itemSoldOut, this);      
      Supreme.app.cart.bind("itemSoldOut", this.itemSoldOut);
      Supreme.app.cart.bind("doneModifyingCart", this.doneModifyingCart);
      this.isLoading = false;
    },
    // Triggered by the cart model when we're done adding or removing something from the cart.
    // Let's this view know that it's ok to be interacted with again.
    doneModifyingCart: function(){
      this.isLoading = false;
    },
    soldOut: function(){
      this.mode = "sold-out";
    },
    itemSoldOut: function(){
      this.soldOut();
      this.render();
    },
    render: function(){      
      // When we render the button we'll determine if it's enabled.
      // There are two options - if the product's can_add_styles is true
      // then there can be multiple styles of the product in the cart.
      // Otherwise the product can only exist in the cart once, regardless of style.
      var isStyleInCart = Supreme.app.cart.hasStyle(this.model.get('selectedStyle'));
      var canAddStyle =   Supreme.app.cart.canAddStyle(this.model.get('selectedStyle'));

      if(canAddStyle){
        if(this.mode == "sold-out"){
          $(this.el).text('sold out');
          // // alert($('#size-options', this.el).length);
          // $('#size-options', this.el).hide();  
          $(this.el).addClass('sold-out');          
          // $('#qty-options', this.el).hide();
        } else {
          $(this.el).text(IS_JAPAN ? 'カートに入れる' : LANG.addToCart);
          this.mode = "adding"; 
          // $('#qty-options', this.el).show();
          // $('#size-options').show();          
        }
      } else {
        if(isStyleInCart){
          // $('#qty-options', this.el).hide();
          $(this.el).addClass('delete');
          $(this.el).text(LANG.removeFromCart);        
          this.mode = "removing";     
          $('#cart-warning').remove();  
          $('#widgets-container').show();             
        }
      }
           
      return this;
    },
    events: {
      click: 'updateCart'
    },
    updateCart: function(){
      if(this.isLoading){
        return;
      }
      this.isLoading = true;
      
      if(this.mode == "adding"){
        $(this.el).text('adding').addClass('adding');
        this.addToCart();
        $.scrollTo(0);
      } else if(this.mode == "removing") {
        if(IS_US){
          $(this.el).text('removing');        
        } else {
          $(this.el).text('...');        
        }
        
        // Remove the X and center the text
        // $(this.el).css({backgroundImage: 'none', paddingLeft: '7px', paddingRight: '6px'});
        this.removeFromCart();
      } else {
        // Button does nothing.
      }
    },
    // Removes this item from the local cart
    // and informs the server.
    removeFromCart: function(){
      var sizeSelect = $('select[name="size-options"]');
      var sizeId = sizeSelect.val();      
      Supreme.app.cart.removeProduct(this.model, sizeId);      
    },
    // this adds size to the cart locally (so we have all the nice meta data),
    // and also sends it to the server.
    // That way the server cookie stays up to date and we can tell if anything sold out.
    addToCart: function(){
      var sizeSelect = $('select[name="size-options"]');
      var sizeId = sizeSelect.val();
      var qty = $('select[name="qty"]').length ? +$('select[name="qty"]').val() : 1;
      if(_.isEmpty(sizeId)){
        alert("Please select a size");
      } else {
        var size = this.model.sizeForId(sizeId);
        Supreme.app.cart.addSize(size, qty);
          $('#cart-warning').remove();// Make sure this thing is gone.
      };      
    }
    
  });
});
$(document).ready(function() {
  CartItemView = Backbone.View.extend({
    tagName: 'tr',
    template: _.template($('#cartItemViewTemplate').html()),
    events: {
      'click td.delete': 'remove',
      'click td.cart-image img': 'jumpToProduct',
      'click td.desc': 'jumpToProduct',
      'change .cart-qty': 'changeQty'
    },
    jumpToProduct: function(){

      // Set the _currentCategory info, for the sake of the Next button.
      // If you're going to a product from here we want Next to be that product's category, not New or something else.
      _currentCategory = singularCategoryName(this.model.category);
      _currentCategoryPlural = this.model.category;
      Supreme.app.navigate("products/" + this.model.product_id + '/' + this.model.style_id, {trigger: true});
    },
    render: function(){
      $(this.el).html($(this.template(this.model)));
      return this;
    },
    changeQty: function(e){
      var newQty = $(e.target).val()
      Supreme.app.cart.changeQty(this.model.product_id, this.model.size_id, newQty);
    },
    remove: function(){
      Supreme.app.cart.removeSize(this.model.product_id, this.model.size_id);
      var self = this;
      $(this.el).animate({opacity: 0}, fadeSpeed, fadeEasingType, function(){
        $(self.el).remove();
      });
    }
  });
});
$(document).ready(function() {
  CartLinkView = Backbone.View.extend({
    tagName: 'div',
    id: 'cart-link',
    initialize: function(){
        _.bindAll(this, "render");      
        this.model.view = this;
        this.model.bind("itemAdded", this.render);
        this.model.bind("doubleItemError", this.handleDoubleItemError)
    },
    render: function(){

      if(Supreme.app.cart.length() == 0){
        $(this.el).hide();
      } else {
        $(this.el).show();
      }

      if (IS_JAPAN) {
        var html = '<a href="#cart" id="goto-cart-link">' + Supreme.app.cart.length() + "</a>";
        html += '<a href="#checkout" id="checkout-now"><span>ご注文手続きへ</span></a>';
      } else {
        var itemsWords = LANG.multiple_items;
        if(Supreme.app.cart.length() == 1){
          itemsWords = LANG.single_item;
        }

        var html = '<a href="#cart" id="goto-cart-link">' + Supreme.app.cart.length() + "</a>";
        html += '<a href="#checkout" id="checkout-now"><span>' + LANG.checkout + '</span></a>';

      }
      
      $(this.el).html(html);            
      return this;

    },
    handleDoubleItemError: function(){
      // TODO - probably need a better visual here.
      alert('You already have added this item to the cart.');
    },
    remove: function(){
      $(this.el).remove();
    }
  });
});
$(document).ready(function() {
  CartView = Backbone.View.extend({
    template:_.template($('#cartViewTemplate').html()),
    el: $('#main')[0],
    initialize: function(){
      this.render = _.bind(this.render, this);
      Supreme.app.cart.bind("itemAdded", this.render);      
    },
    // Accepts an optional error message.
    render: function(message){
      if(Backbone.history.fragment != "cart"){
        return;
      }
      
      $(this.el).empty();
      var self = this;

      $(this.el).html(this.template(this.model.toJSON()));
      
      // If items in the cart are sold out we'll always show the error message.
      // Clear it out before hand though so we don't double up.
      $('.from-sold-out-items', this.el).remove();
      
      if(Supreme.app.cart.lastError == "dup"){
        $("table", this.el).before($('<div id="error">You have previously ordered this item(s). There is a limit of 1 style per product.</div>'));
      } else if (Supreme.app.cart.lastError == "blacklisted") {
        if (IS_JAPAN)
          $('table', this.el).before($('<div id="error">利用規約に従いまして、お客様からのご注文はお断りさせて頂きます。</div>'));
        else
          $("table", this.el).before($('<div id="error">You have previously ordered this item(s). There is a limit of 1 style per product.</div>'));
      } else if (Supreme.app.cart.lastError == "canada"){ 
        $("table", this.el).before($('<div id="error">Some items in your cart are sold only in the U.S. (no Canada shipping).</div>'));
      } else if (Supreme.app.cart.lastError == "blocked_country"){ 
        $("table", this.el).before($('<div id="error">Some items in your cart are sold only in the EU.</div>'));
      } else if(Supreme.app.cart.lastError == "outOfStock"){
        $("table", this.el).before($('<div id="error">' + soldOutMessage + '</div>'));        
      } else {
        $('#error', this.el).remove();
      }

      // Fill in the cart items.
      // We keep this data in the cart.
      var numSoldOut = 0;
      var numNotSoldOut = 0;
      // for(var i = 0; i < localStorage.length; i++){
      //   var sizeId = localStorage.key(i);  
      //   if(!storageKeyIsProduct(sizeId)){continue;} // This junk key kept appearing in localStorage.
      //   var size = Supreme.app.cart.getSizeFromLocalStorage(sizeId);
        
      //   // Is this size sold out? Flag it befoew it gets rendered.
      //   if(!_.isNull(sessionStorage.getItem('out_of_stock_' + sizeId))){
      //     size.set('out_of_stock', true);
      //     numSoldOut++;
      //   } else {
      //     numNotSoldOut++;
      //     size.set('out_of_stock', false);
      //   }
        
      //   var itemView = new CartItemView({model: size});
      //   $('table tbody', this.el).append(itemView.render().el);
      // }


      var count = 0;
      Supreme.app.cart.getServerContents(function(cart){
        $('table tbody', this.el).empty();
        for (var key in cart) {
           if (cart.hasOwnProperty(key)) {
              console.log(key, cart[key]);
              var itemView = new CartItemView({model: cart[key]});
              $('table tbody', this.el).append(itemView.render().el)
              count++;
           }
        }
        $('#cart_item_count').text(count)

        if(count == 1){
          $('cart_item_count_singular').show();
        } else {
          $('cart_item_count_multiple').show();
        }
      });


      // If all the items are sold out we'll show that error.
      // Don't bother if we're already showing it from the checkout error.
      if( numSoldOut > 0 && Supreme.app.cart.lastError != "outOfStock"){
        $("table", this.el).before($('<div id="error" class="from-sold-out-items">' + soldOutMessage + '</div>'));
      }
      
      // How could this happen that the user is on the cart page but it's empty?
      // It's because removing an item here via the CartItemView X button
      // triggers a re-rendering of this view.
      if(Supreme.app.cart.length() == 0){
        // Empty? Bounce 'em.
        _.delay(function(){
            Supreme.app.navigate("#", {trigger: true});
        }, 500);
      }
      this.setSubtotal();
    },
    setSubtotal: function(){
      var itemTotal = Supreme.app.cart.itemTotal();
      $('#cart-total span.cart-subtotal', this.el).text(formatCurrency(itemTotal));
      if(IS_EU){
        $('#cart-total span.cart-subtotal-euro', this.el).text(formatCurrency(GBPtoEuro(itemTotal), '€', true));        
      }
      
    }    
  });
});
$(document).ready(function() {
  // View of all categories.
  CategoryCollectionView = Backbone.View.extend({
    
    template:_.template(categoryListTemplate),
    initialize: function(){
      var that = this;
      this._categoryListViews = [];
      
      var sortedCollection = this.collection.sortBy(function(c){
        return _.indexOf(categoryOrder, c.get('name'));
      });
      
      _.each(sortedCollection, function(category){
        that._categoryListViews.push(new CategoryListView({model: category, id: category.get('name').toLowerCase() + '-category'}));
      });
    },
    render: function(){
      var self = this;
      self.updateContent();
    },
    updateContent: function(){
      var self = this;      
      $(self.el).html(self.template);    
      var d = $('<ul></ul>');
      _(self._categoryListViews).each(function(categoryListView) {
        d.append(categoryListView.render().el);
      });      
      mixpanelTrack('Shop View', {'Shop View Type': 'Mobile Category'});
      $('#categories-list', this.el).append(d);
    }
  });
});
$(document).ready(function() {
  // View of single category, in their list view.
  CategoryListView = Backbone.View.extend({
    tagName: "li",
    className: 'selectable',
    events: {
         click: "select"
    },
    render: function() {
      $(this.el).html("<span>" + this.model.get('name') + "</span>");
        return this;
    },
    select: function(){
      _currentCategory = singularCategoryName(this.model.get('name')); // if you tap into a category, remember the category name we tapped into, for Next Product button purposes.
      _currentCategoryPlural = this.model.get('name');
      Supreme.app.navigate("categories/" + this.model.get('name'), {trigger: true});
      mixpanelTrack('Shop View', {'Shop View Type': _currentCategory}); 
    } 
  });
});
$(document).ready(function() {
  // View of all products in a category.
  CategoryProductsView = Backbone.View.extend({
    template: _.template(productListTemplate),
    initialize: function(){
      var self = this;
      this._productListViews = [];
      this.collection.each(function(product){
        self._productListViews.push(new ProductListView({model:product}));
      });
    },
    render: function(){
      var self = this;
      console.log(this.el)
      $(this.el).animate({opacity: 0}, fadeSpeed, fadeEasingType, function(){
        self.updateContent();
      });
    },
    updateContent: function(){
      var self = this;      
      $(this.el).html(this.template);
      $('h2', this.el).text(this.model.get('name'));
      var newUl = $("<ul>");      
      _(this._productListViews).each(function(productListView){
        newUl.append(productListView.render().el);
      });   
      $('ul', self.el).replaceWith(newUl);
      $(self.el).animate({opacity: 1}, fadeSpeed, fadeEasingType);
    }
  });
  
});
$(document).ready(function() {
  ChargeErrorViewTemplate = Backbone.View.extend({
    tagName: 'div',
    template: _.template($('#chargeErrorTemplate').html()),
    render: function(){
      $(this.el).html($(this.template(this.model)));
      return this;
    }
  });  
});
$(document).ready(function() {
  CheckoutView = Backbone.View.extend({
    template:_.template($('#checkoutViewTemplate').html()),
    initialize: function(){
      this.checkout_zipcodes = {};
      if (!IS_JAPAN) {
        _.bindAll(this, 'countryChanged');
        this.model.bind('change:order_billing_country', this.countryChanged);
      }
      if(IS_US){
        _.bindAll(this, 'zipcodeAutofill');   
        // _.bindAll(this, 'creditCardKeyUp');   
      }
      
      _.bindAll(this, 'creditCardTypeChanged');
      this.model.bind('change:credit_card_type', this.creditCardTypeChanged);      
      _.bindAll(this, 'stateChanged');
      this.model.bind('change:order_billing_state', this.stateChanged);      
      this.model.bind('change:order_billing_zip', this.stateChanged);      
      this.model.bind('change:obz', this.stateChanged);      
      _.bindAll(this, 'renderCheckoutErrors');      
      this.model.bind('checkoutErrors', this.renderCheckoutErrors); 
      _.bindAll(this, 'stateChanged');      
      
      _.bindAll(this, 'renderDuplicateOrderError');
      this.model.bind('dupError', this.renderDuplicateOrderError);
      
      _.bindAll(this, 'renderOutOfStockError');
      this.model.bind('outOfStockError', this.renderOutOfStockError);      
      
      _.bindAll(this, 'renderChargeError');
      this.model.bind('chargeFailed', this.renderChargeError);      
      
      this.bind('totalsRecalculationNeeded', this.updateTotals);
      if (IS_JAPAN)
        this.rememberedFields = ['#order_billing_name', '#order_billing_last_name', '#order_email', '#order_tel', '#order_billing_address', '#order_billing_city', '#order_billing_state', '#order_billing_zip, #obz'];
      else
         this.rememberedFields = ['#order_billing_name', '#order_email', '#order_tel', '#order_billing_address', '#order_billing_address_2', '#order_billing_city', '#order_billing_state', '#order_billing_zip, #obz', '#order_billing_country'];
         
    },
    renderChargeError: function(fromBot){
      // If we had shown the Use Credit buttons remove them, we're back to the old buttons.
      $('#store_credits').remove();
      $('#checkout-buttons').show();
      if(fromBot){
        Supreme.app.navigate("#chargeErrorBot", {trigger: true});
      } else {
        Supreme.app.navigate("#chargeError", {trigger: true});
      }
    },
    populateAddressFromCookie: function(){
      if(_.isNull(readCookie('js-address'))){return;}
      var addressCookieBits = decodeURIComponent(readCookie('js-address')).split('|');
      for(var i = 0; i < addressCookieBits.length; i++){
        $(this.rememberedFields[i], this.el).val(addressCookieBits[i]);
      }
      // Need to tell the model what's what with the remembered values, for tax and shipping purposes.
      this.model.set('order_billing_state', $('#order_billing_state', this.el).val());
      this.model.set('order_billing_country', $('#order_billing_country', this.el).val());
    },
    render: function(){
      $(this.el).html(this.template());
      var self = this;      
      
      $('#remember_address_label', this.el).click(function(e){
        // Just need a fake event on these labels to get them to work...
      });
      $('#order-terms-label', this.el).click(function(e){
        // Just need a fake event on these labels to get them to work...
      });

      $('#order-terms-label a', this.el).bind('click', function(e){
          var staticContentView = new StaticContentView();
          staticContentView.render('terms');
          window.scroll(0, 0);
          e.preventDefault();
      });

      if (IS_JAPAN) {
        $("#order_billing_state", this.el).html($('#checkoutViewStatesTemplate').html());
        if (Supreme.app.cart.hasItemsPreventingCOD()){
          $('#credit_card_type option[value="cod"]', this.el).remove();
        }
      }

      if (IS_US) {
        if (Supreme.app.cart.hasItemsPreventingCanada()) {
          $('#order_billing_country option[value="CANADA"]', this.el).remove();
          $('#order_billing_state option[value="HI"]', this.el).remove();
          $('#order_billing_state option[value="AK"]', this.el).remove();
          $('#order_billing_state option[value="PR"]', this.el).remove();
          $('#order_billing_state option[value="GU"]', this.el).remove();
        }
      }


      if(window.navigator.standalone){
        // Hide the Remember Address checkbox if we're in standalone mode.
        $('#remember_address', this.el).parent().parent().hide();
        $('#remember_address', this.el).parent().parent().after("<br />"); // Sneak in a little cheap line break for padding purposes.
        
        // Record that this came from stand alone mode.
        $('form', this.el).append('<input type="hidden" name="is_from_mobile_standlone" value="1" />');
      }      

      if (window.pushNotificationId)
        $('form', this.el).append('<input type="hidden" name="push_notification_id" value="' + window.pushNotificationId + '" />');

      if (window.ClickedPushNotificationId)
        $('form', this.el).append('<input type="hidden" name="clicked_push_notification_id" value="' + window.ClickedPushNotificationId + '" />');

			if(navigator.userAgent.match(/Android/i)){
				$('form', this.el).append('<input type="hidden" name="is_from_android" value="1" />');
			}

      if(navigator.userAgent.match(/SupremeAndroidApp/i)){
        $('form', this.el).append('<input type="hidden" name="is_from_android_app" value="1" />');
      }

			// Catch the supreme-native version and save it.
			// Should be something like 'Supreme-native/2 (iPad Simulator; iOS 7.0; Scale/1.00, language: fr, locale: GB)'
      if(window.IOS_APP){
        $('form', this.el).append('<input type="hidden" name="is_from_ios_native" value="1" />');
      }

      // For some reason these events weren't binding in the events hash.
      $('input, select', this.el).bind('focus', this.fieldFocusChanged);
      $('input, select', this.el).bind('blur', this.fieldFocusChanged);      
      $('#remember_address', this.el).bind('change', function(){
        // We track whether Remember Me was checked in a different cookie.
        // This is because we need to know whether to auto-check that checkbox the next
        // time the page is loaded.
        // Can't rely on just checking the address cookie, since that gets
        // set with every key change, and gets killed at checkout unless this is checked.
        if($(this).prop('checked')){
          createCookie('remember_me', 1, 182);
        } else {
          eraseCookie('remember_me');
        }
      });
      var subtotalAmt = Supreme.app.cart.itemTotal();
      $('#subtotal', this.el).text(formatCurrency(subtotalAmt));
      if(IS_EU){
        $('#subtotal_eu', this.el).text(formatCurrency(GBPtoEuro(subtotalAmt), '€', true));
      }      
     
      if (!IS_JAPAN)
        this.countryChanged();   


      // Were any of  these country pre-selected? Trigger the reclaculate.
      if(IS_EU){
        var preselected = $('#order_billing_country', this.el).find('option[selected=selected]');
        if(preselected.length > 0){
          this.model.set('order_billing_country', $('#order_billing_country', this.el).val());
        }
      }
      
      this.populateAddressFromCookie();
      this.trigger('totalsRecalculationNeeded');     
          
      // Is the address cookie saved? Check that box.
      if(!_.isNull(readCookie('remember_me'))){
        $('#remember_address', this.el).attr('checked', 'checked');
      }
      
      $('input, select', this.el).on('focus', function(e){
        // Remove all the others.
        $('table', this.el).find('label').removeClass('active');
        $(this).closest('tr').find('label:not(#address_2_spaceholder)').addClass('active');
        // The masking plugin broke this on the tel and CC fields, so we have to do this manually there
      });
      
      if(IS_US){
        $('#order_billing_zip, #obz', this.el).bind('keyup', this.zipcodeAutofill);
        $('#order_tel').mask('000-000-0000'); 
        // $('#credit_card_n', this.el).bind('keyup', this.creditCardKeyUp);
        this.setupInlineValidation();
      }

      this.maskCreditCardField();

      if (USE_ADDRESSY && IS_US) {
        setTimeout(function(){
         var fields = [
            { element: "order_billing_address", field: "Line1" },
            { element: "order_billing_address_2", field: "Line2", mode: pca.fieldMode.POPULATE },
            { element: "order_billing_city", field: "City", mode: pca.fieldMode.POPULATE },
            { element: "order_billing_state", field: "Province", mode: pca.fieldMode.POPULATE },
            { element: "obz", field: "PostalCode" },
            { element: "order_billing_country", field: "Country", mode: pca.fieldMode.COUNTRY }
         ];

          var options = {
              key: "KD23-WG31-MF11-GF79",
              search: { countries: "USA, CAN" },
              setCountryByIP: true,
              suppressAutocomplete: false
           };

           var control = new pca.Address(fields, options);
           control.listen("populate", function(address, variations){
              self.trigger('totalsRecalculationNeeded');
              $('#order_billing_state').selectric('refresh');
           });
        }, 1000);


      }

      return this;
    },
    captcha: function() {
      var that = this;
      window.recaptchaCallback = function() {
        that.submitFormAfterCaptcha();
      }

      if ($('#g-recaptcha').length > 0)
        this.recaptcha_id = grecaptcha.render('g-recaptcha', {'sitekey': $('#g-recaptcha').data('sitekey'), 'size': 'invisible', 'badge': 'inline', 'callback': 'recaptchaCallback'});

    },
    events: {
      'change input': 'fieldChanged',
      'change select': 'fieldChanged',
      'submit form': 'submitForm',
      'click #cancel_checkout': 'cancelCheckout'
    },
    // This is the zipcode autofiller. US only.    
    zipcodeAutofill: function(e){
      var self = this;
      if($('#order_billing_country').val() == 'USA'){
        var original_zip = $('#order_billing_zip, #obz').val();
        var zip = original_zip;
        if(zip.length >= 4){
          if(zip.length > 4){
            zip = zip.substring(0,4); // if the zip is longer than 4 make it 4 so we can still get the json.
            $.ajax({
              url: "//supreme-images.s3.amazonaws.com/us-zipcodes/" + zip + ".js",
              jsonpCallback: 'w',
              success: function(data){
                self.checkout_zipcodes[zip] = data; // stash the data away                
                if(original_zip.length == 5){
                  // find the matching zipcode
                  for(var i = 0; i < data.length; i++){
                    if(data[i].zipcode == original_zip){
                      $('#order_billing_city').val(data[i].city);
                      $('#order_billing_state').val(data[i].state);
                      self.trigger('totalsRecalculationNeeded');
                      $('#order_billing_state').selectric('refresh');
                    }
                  }
                }
              },
              dataType: 'jsonp'});
            }
          }
        }
    },
    cancelCheckout: function(e){
      // Does nothing unless this is the native app.
      if(window.IOS_APP_NATIVE){
        location.href = 'supreme://index';
        e.preventDefault();
        return;
      } else {
        return true;
      }
      
    },
    // We record every field change during the session,
    // so when you reload the page we can refresh that content.
    // If they didn't check the Remember Me checkbox we'll kill this cookie at checkout.
    rememberAddress: function(fields){
      var cookie = _.map(fields, function(e){
        return encodeURIComponent($(e).val());
      });
      createCookie('js-address', cookie.join('|'), 182); // 6 months about.
    },
    renderDuplicateOrderError: function(){
      // Dupe error? Say so.
      Supreme.app.navigate("cart", {trigger: true});              
    },
    renderOutOfStockError: function(){      
      // Native app sends you back to the cart view in the app.
      if(window.SUPPORT_SUPREME_PROTOCOL){
        window.location = 'supreme://cart';
      } else {
        // Out of stock error error? Say so.
        Supreme.app.navigate("cart", {trigger: true});        
      }
      
    },
    // Render the errors we get from the model on the form.
    renderCheckoutErrors: function(errors){
      $('#mobile_checkout_form').data('credit_verified', 0); // Cancel out the credit verified flag so if we're going to have to re-submit for whatever reason we'll check again.
      // If we had shown the Use Credit buttons remove them, we're back to the old buttons.
      $('#store_credits').remove();
      $('#checkout-buttons').show();
      
      
      var self = this;
      
      var reToSkip = new RegExp("Shipping|Type|Last|First|is not included in the list");
      
      // Clear out previous errors.
      $('.unhappy', this.el).removeClass('unhappy')
      $("#checkout-errors", this.el).hide();  
      $("#credit-card-checkout-errors", this.el).hide();   
      $('p.error', this.el).removeClass('error');
      $('.checkbox-container label', this.el).removeClass('error');
      $('tr.error', this.el).removeClass('error');
      
      
      var creditCardErrorMessagesForForm = [];
      
      // Apply the error styles for @order errors.
      var orderErrorMessage = {};
      $('.msg', self.el).remove();
      if(!_.isUndefined(errors.order)){
        _.each(errors.order, function(errors, field){
          var msg = errors.join(', ');
          // Skip certain errors.
          if(!msg.match(reToSkip)){
            if(orderErrorMessage.hasOwnProperty(field)){
              orderErrorMessage[field].push(errors);
            } else {
              orderErrorMessage[field] = errors;  
            }
            
            $('#order_' + field, self.el).closest('td').addClass('error unhappy');
          }
        });        
        
        // Show the global error here if we have errors,
        // unless it's just one error and that's the terms error.
        if(IS_JAPAN && Object.keys(orderErrorMessage).length > 0){
          if(!(Object.keys(orderErrorMessage).length == 1 && !_.isUndefined(orderErrorMessage.terms))){
          $("#checkout-errors", self.el).html(" 入力漏れ、もしくは入力内容に誤りがあります。<br />Eメールアドレス、電話番号、郵便番号は半角英数字でご記入ください。").show();                                         

          }

        }        
        
      }

      
      // Credit card errors:
      var creditCardErrorMessage = {};
      if(!_.isUndefined(errors.credit_card)){

        _.each(errors.credit_card, function(errors, key){
          var msg = errors.join(', ');
          // Skip certain errors.
          if(!msg.match(reToSkip)){
            if(creditCardErrorMessage.hasOwnProperty(key)){
              creditCardErrorMessage[key].push(errors);
            } else {
              creditCardErrorMessage[key] = errors;
            }
            
            var elId = '#credit_card_' + key;
            if(key == 'verification_value'){
              elId = '#cvv-container input';
            }
            if(key == 'number'){
              elId = '#cn';
            }
            $(elId, self.el).closest('td').addClass('error');
          }          
          

        });        
      }
      
        var underScoreRe = new RegExp("_", "g");
        var billingRe = new RegExp("billing", "g");
        var numberRe = new RegExp("^number", "g");        
        var yearExpiredRe = new RegExp("year", "g");
        var CVVRe = new RegExp("verification value", "g");
        
        // Handle the billing info field errors.
        _.each(orderErrorMessage, function(messages, field){
          var msg = messages.join(', ');

          var printable_field = field.replace(underScoreRe, " ");
          printable_field = printable_field.replace(billingRe, "");     

          if(field == "terms"){ // Terms checkbox gets a special treatment.
            $('#order-terms-label', self.el).append('<span class="msg">' + (IS_JAPAN ? '利用規約に同意してください' : printable_field + ' ' + msg) + '</span>'); 
          } else if (IS_JAPAN) {
            $('#order_' + field, self.el).parent().parent().addClass('error');
          } else if (IS_EU){ // EU doesn't get the field name in the message. was too long.
            $('#order_' + field, self.el).parent().append('<span class="msg">' + msg + '</span>');             
          } else {
            $('#order_' + field, self.el).parent().append('<span class="msg">' + printable_field + ' ' + msg + '</span>')
          }
        });
        

        
        _.each(creditCardErrorMessage, function(messages, field){
          var msg = messages.join(', ');

          // CLean up some error messages.
          var printable_field = field.replace(underScoreRe, " ");
          printable_field = printable_field.replace(billingRe, "");
          printable_field = printable_field.replace(yearExpiredRe, "date");                    
          printable_field = printable_field.replace(CVVRe, "");     
          printable_field = printable_field.replace(numberRe, "");               
          
          var fieldElement;

          if(field == 'number'){
            fieldElement = $('#credit_card_n', self.el);
            creditCardErrorMessagesForForm.push("カード番号が無効です。");
          } else if(field == "type"){
            fieldElement = $('#credit_card_type', self.el);            
          } else if(field == 'verification_value'){
            creditCardErrorMessagesForForm.push("CVV番号が無効です。");            
            fieldElement = $('#credit_card_cvv', self.el);
          } else if(field == 'year'){
            creditCardErrorMessagesForForm.push("有効期限切れです。");                        
            fieldElement = $('#credit_card_month', self.el);            
          }
          
          if(fieldElement){
            if (IS_JAPAN){
              fieldElement.closest('tr').find('td').addClass('error');
            } else {
              fieldElement.parent().append('<span class="msg">' + printable_field + ' ' + msg + '</span>');
              fieldElement.addClass('unhappy');
            }
          }

        });

        if (creditCardErrorMessagesForForm.length > 0 && IS_JAPAN){
          $("#credit-card-checkout-errors", this.el).text(creditCardErrorMessagesForForm.join(' ')).show();
        }

        // AVS error? We'll just have {avs: true}.
        // Show that message and scroll to it.
        if(errors.avs){
          $("#credit-card-checkout-errors", this.el).text(LANG.avs_error).show();
          $('#credit_card_n', self.el).addClass('unhappy');
        }

        // CC errors and no address errors, or AVS error? Scroll down there.
        if(errors.avs || (Object.keys(creditCardErrorMessage).length > 0 && Object.keys(orderErrorMessage).length == 0)){
          window.scrollTo(0, $('#credit-card-information-header', this.el).offset().top);
        }

        // 1 address error and it's the terms, no CC errors? Scroll down there.
        if(Object.keys(creditCardErrorMessage).length == 0 && Object.keys(orderErrorMessage).length == 1 && orderErrorMessage.hasOwnProperty('terms')){
          window.scrollTo(0, $('#order-terms-label', this.el).offset().top);  
        }
    },
    disableSubmitButton: function(){
      $('#submit_button').attr('disabled', 'disabled').addClass('loading');
    },
    enableSubmitButton: function(){
      $('#submit_button').removeAttr('disabled').removeClass('loading');
    },
    hideKeyboard: function(){
      // The blinking cursor was sometimes showing through the loading screen.
      // This input field is hidden offscreen and it will get the focus.
      // Just blurring the existing fields wasn't doing it.
      // Also hides the keyboard.      
      $('#hidden_cursor_capture', this.el).focus();
    },
    submitForm: function(e){

      this.hideKeyboard();

      if ($('#g-recaptcha').length > 0 && !$('textarea[name="g-recaptcha-response"]').val()) {
        grecaptcha.execute(this.recaptcha_id);
        return false;
      } else {
        this.submitFormAfterCaptcha()
      }
      
      
      e.preventDefault();
    },
    cookieSubValue: function() {
      var cookieProducts = JSON.parse(decodeURIComponent(readCookie('pure_cart')));
      delete cookieProducts.cookie;

      _.each(cookieProducts, function(v, size_id){
        if(_.isNull(localStorage.getItem(size_id.toString()))){
          delete cookieProducts[size_id];
        } else if (Supreme.app.cart.quantityForSize(size_id) < v) {
          cookieProducts[size_id] = Supreme.app.cart.quantityForSize(size_id);
        }
      });
       
      // If anything was removed we'll re-assemble that cookie to pass in, now scrubbed.
      return encodeURIComponent(JSON.stringify(cookieProducts));

    },
    submitFormAfterCaptcha: function(e) {
      if (window.pookyCallback)
        window.pookyCallback();

      // Need to copy the running cart cookie over to an input field to send back to the server
      // on our https domain.
      // We'll also take this opportunity to make sure that only items in localstorage and the cookie
      // are getting submitted, in case the server thinks we have something we don't.
      $('#cookie-sub').val(this.cookieSubValue());

      var self = this;

      if($('#mobile_checkout_form').data('credit_verified') == '1'){
        // var tt = new TrackTiming('Mobile application', 'Checkout');
        // Start loading.
        var containerOffset = $(this.el).offset();
        $('#checkout-loading', this.el).css({
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          opacity: 0
        });
        $('body').addClass('checkout-loading');
        $('#cart-link').hide();
        self.hideKeyboard();
        $('#checkout-loading', this.el).show();
        $('#checkout-loading', this.el).animate({opacity: 1}, 0, 'ease-out', function(){
          $('#checkout-loading').find('.progress-bar').addClass('go');
          window.scrollTo(0, 0);
          window.pollOrderStatus = function(slug) {
            var checkStatus = function() {
              $.ajax({
                type: 'GET',
                url: '/checkout/' + slug + '/status.json',
                xhrFields: {
                  withCredentials: true
                },
                success: function(data) {
                  if (data['status'] == "queued")
                    window.setTimeout(checkStatus, 10000);
                  else
                    handle_checkout_success(data);
                },
                error: function() {
                  window.setTimeout(checkStatus, 20000);
                }
              });
            }
            window.setTimeout(checkStatus, 10000)
          }

          var handle_checkout_success = function(body) {
            $('#cart-link').show()
            $('body').removeClass('checkout-loading');
            var okToFade = self.model.processFormResponse(body);
            if(okToFade){
              $('#checkout-loading', this.el).animate({opacity: 0}, fadeSpeed, fadeEasingType, function(){
                $(this).hide();
              });            
            }
            self.enableSubmitButton();            
          }


          $.ajax({
            type: 'POST', // defaults to 'GET'
            url: $('#mobile_checkout_form').attr('action'),
            data:  $('#mobile_checkout_form').serializeArray(),
            dataType: 'json',
            timeout: 60000, // Sometimes response status of 0 were being returned, which would happen in a timeout. I'm trying to set a timeout to see if that prevent it, otherwise i don't know what the issue is.
            success: function(body) {
              if (body.status == "queued")
                pollOrderStatus(body.slug);
              else
                handle_checkout_success(body);

            },
            xhrFields: {
              withCredentials: true
            },
            error: function(xhr, errorType, error) {
              $('#cart-link').show()
              // Connection error? Assume charge failed.
              logError('submitForm ajax error', {
                statusText: xhr.statusText,
                status: xhr.status,
                errorType: errorType,
                error: error
              });        
              
              self.model.trigger('chargeFailed');
              self.enableSubmitButton();
            }
          });        
        });
        
      } else { // Have we not verified store credit yet? Do that now.
        // Temporarily disable the form so we can check on the store credit verification without risking multiple submissions.
        self.disableSubmitButton();
        $.ajax({
          type: 'GET',
          url: '/store_credits/verify',
          data: { email: $('#order_email').val() },
          dataType: 'html',
           success: function(data){
             $('#mobile_checkout_form').data('credit_verified', '1');
            $('#store_credits').remove(); // In case we already added it.
            $('#checkout-buttons').hide(); // Hide the regular buttons.
            $('#checkout-buttons').after($(data));
            $('#store_credits').show();
            $.scrollTo($('#store_credits').offset().top); // Scroll down to the new buttons.
            
            // Yes, use store credit.
            $('#store_credit').click(function(ev){
              // get the store credit ID from the server and put it in our hidden field.
              $('#store_credit_id').val($('#store_credit').attr('store_credit_id'));
              $('#mobile_checkout_form').data('credit_verified', '1');
              self.submitFormAfterCaptcha();
              self.enableSubmitButton();              
              ev.preventDefault();
              ev.stopImmediatePropagation();
            });
            
           // Yes, use store credit.
            $('#no_store_credit').click(function(ev){
              $('#mobile_checkout_form').data('credit_verified', '1');
              self.submitFormAfterCaptcha();
              self.enableSubmitButton();
              ev.preventDefault();
              ev.stopImmediatePropagation();
            });            
          },
          error: function(xhr, errorType, error){
            // Server returns a 404 if it can't find any store credit for this person.
            // Just submit the actual payment form.
            $('#mobile_checkout_form').data('credit_verified', '1');
            self.submitFormAfterCaptcha();
            self.enableSubmitButton();
          }
        });        
        
      }
 

    },
    fieldFocusChanged: function(e){
      if($(e.target).siblings('label').hasClass('error')){
        return;
      }
      if(e.type == "focus"){
        $(e.target).siblings('label').addClass('focused');
      } else if(e.type == "blur"){
        $(e.target).siblings('label').removeClass('focused');
      } else {}
    },
    fieldChanged: function(e){
      this.model.set(e.target.id, $(e.target).val());
      this.rememberAddress(this.rememberedFields);
    },
    // When the credit card types changes to COD we need to hide the payment fields.
    creditCardTypeChanged: function(e){
      var type = $('#credit_card_type', this.el).val();
      if(type == 'cod') {
        $('#credit_card_number_row', this.el).hide();
        $('#exp_date_row', this.el).hide(); 
        $('#cvv_row', this.el).hide();      
        $('#paypal_info').hide(); 
      } else if(type == 'paypal'){
        $('#credit_card_number_row', this.el).hide();
        $('#exp_date_row', this.el).hide(); 
        $('#cvv_row', this.el).hide();
        $('#paypal_info').show();
      } else {
        $('#paypal_info').hide();
        $('#credit_card_number_row', this.el).show();
        $('#exp_date_row', this.el).show(); 
        $('#cvv_row', this.el).show();        
        

        this.maskCreditCardField();

      }
      this.trigger('totalsRecalculationNeeded');               
    },
    // creditCardKeyUp: function(e) {
    //   this.maskCreditCardField();
    // },
    creditCardTypeFromNumber: function(num) {
      // first, sanitize the number by removing all non-digit characters.
      num = (num || '').replace(/[^\d]/g,'');
      // now test the number against some regexes to figure out the card type.
      if (num.match(/^5[1-5]\d$/)) {
        return 'mastercard';
      } else if (num.match(/^4\d/) || num.match(/^4\d/)) {
        return 'visa';
      } else if (num.match(/^3[47]\d/)) {
        return 'american_express';
      } else if (num.match(/^35(28|29|[3-8]\d)\d$/)) {
        return 'jcb';
      }
      return 'UNKNOWN';
    },
    maskCreditCardField: function(){
      var self = this;
      var options =  {
        autoclear: false,
        onKeyPress: function(cep, e, field, options) {
          var type = IS_US ? self.creditCardTypeFromNumber($('#credit_card_n').val()) : $('#credit_card_type', self.el).val();
          var masks = ['9999 999999 99999', '9999 9999 9999 9999'];
          var mask = type == 'american_express' ? masks[0] : masks[1];
          $('#credit_card_n', self.el).mask(mask, options);
      }};
      $('#credit_card_n', this.el).mask('9999 9999 9999 9999', options)
    },
    countryChanged: function(e){
      if(this.model.get('order_billing_country') == "USA"){
        $('label#state_label', this.el).text('state');
        $("#order_billing_state", this.el).html($('#checkoutViewStatesTemplate').html())
        $('#intl-shipping-info', this.el).hide();  
        
        // Swap in the "US" bit of the phone number error it it's present.
        var errors = $('#checkout-errors', this.el).text();
        var re = new RegExp("10-digit phone number");
        errors = errors.replace(re, "10-digit us phone number");      
        $('#checkout-errors').text(errors);        
              
      } else {

        $('label#state_label', this.el).text('province');        
        $("#order_billing_state", this.el).html($('#checkoutViewProvincesTemplate').html())
        $('#intl-shipping-info', this.el).show();
        
        // Swap out the "US" bit of the phone number error it it's present.
        var errors = $('#checkout-errors', this.el).text();
        var re = new RegExp("10-digit us phone number");
        errors = errors.replace(re, "10-digit phone number");      
        $('#checkout-errors').text(errors);        
        
        
        if(IS_EU){
          if(Supreme.app.cart.hasVat(this.model.get('order_billing_country'))){
            $('.eu #checkout-form span.field').removeClass('no-vat');  
          } else {
            $('.eu #checkout-form span.field').addClass('no-vat');  
          } 
        }
      }
      this.trigger('totalsRecalculationNeeded');         
    },
    setShippingTotal: function(){
      var amt = Supreme.app.cart.shippingTotal(this.model.get('order_billing_country'), this.model.get('order_billing_state'));
      // Only can set the shipping total if we have a state/country.
      
      if(FREE_SHIPPING && amt == 0){
          $('#shipping', this.el).addClass('free-shipping').text(IS_JAPAN ? "無料" : 'free shipping');
          if(IS_EU){
            $('#shipping_eu', this.el).text('');
          }          
       
      } else {
        $('#shipping', this.el).removeClass('free-shipping').text(formatCurrency(amt));
        if(IS_EU){
          $('#shipping_eu', this.el).text(formatCurrency(GBPtoEuro(amt), '€', true));
        }        
      }
      

      
    },
    setOrderTotal: function(){
      var amt = Supreme.app.cart.orderTotal(this.model.get('credit_card_type'),this.model.get('order_billing_country'), this.model.get('order_billing_state'));
      $('#total', this.el).text(formatCurrency(amt));
      if(IS_EU){
        $('#total_eu', this.el).text(formatCurrency(GBPtoEuro(amt), '€', true));
      }
      
    },
    stateChanged: function(){
      this.trigger('totalsRecalculationNeeded');
    },
    setVATDiscount: function(){
      var total = Supreme.app.cart.vatDiscount(this.model.get('order_billing_country'), this.model.get('order_billing_state'));    
      if(total == 0){
        $('#vat-discount-container', this.el).hide();
        $('#vat-discount-total', this.el).text('');
      } else {
        $('#vat-discount-container', this.el).show();
        $('#vat-discount-total', this.el).text('-' + formatCurrency(total));
        $('#vat-discount-total_eu', this.el).text('-' + formatCurrency(GBPtoEuro(total), '€', true));
      }
    },
    setCODTotal: function(){
      if($('#credit_card_type', this.el).val() == 'cod') {
        $('#cod', this.el).text(formatCurrency(Supreme.app.cart.codTotal('cod')));        
        $('#cod_row', this.el).show();        
      } else {
        $('#cod_row', this.el).hide();
        $('#cod', this.el).text('');
      }
    },
    setTaxTotal: function(){
      var total = Supreme.app.cart.taxTotal(this.model.get('order_billing_country'), this.model.get('order_billing_state'));
      if(total != 0){
        $('#sales-tax-container', this.el).show();
        $('#sales-tax-container #sales-tax-total', this.el).text(formatCurrency(total));        
      } else {
        $('#sales-tax-container', this.el).hide();        
        $('#sales-tax-container #sales-tax-total', this.el).text("");                
      }

    },
    updateTotals: function(){
      var self = this;
      if (IS_EU && $('#order_billing_country').length) {
        $.ajax({
          type: 'GET',
          url: '/checkout/totals_mobile.js',
          data: { 'order[billing_country]': $('#order_billing_country').val(), 'cookie-sub': this.cookieSubValue(), mobile: true},
          dataType: 'html',
          success: function(data){
            $('#totals_response').replaceWith(data);
          },
          error: function(xhr, errorType, error){
            // Fallback
            self.setShippingTotal();
            self.setOrderTotal();   
            self.setTaxTotal(); 
            self.setVATDiscount();
          }
        });        

      } else if (IS_US && $('#order_billing_state').length) {
        $.ajax({
          type: 'GET',
          url: '/checkout/totals_mobile.js',
          data: { 'order[billing_country]': $('#order_billing_country').val(), 'cookie-sub': this.cookieSubValue(), 'order[billing_state]': $('#order_billing_state').val(), 'order[billing_zip]': $('#order_billing_zip, #obz').val(), mobile: true},
          dataType: 'html',
          success: function(data){
            $('#totals_response').replaceWith(data);
            self.watchSurchageInfo();

            $('.tax-tooltip', this.el).click(function(e){
              window._gaq.push(['_trackEvent', 'estimated-tax-info', 'mobile']);
              $('#estimated-tax-info').toggle();
            });

            $('#estimated-tax-info a').bind('click', function(e){
                var staticContentView = new StaticContentView();
                staticContentView.render('terms');
                setTimeout(function(){
                  window.scrollTo(0, $('#tax_terms').offset().top - 10);
                }, 100);
                e.preventDefault();
            });
          },
          error: function(xhr, errorType, error){
            // Fallback
            self.setShippingTotal();
            self.setOrderTotal();   
            self.setTaxTotal(); 
            self.setVATDiscount();
          }
        });  
      } else {
        this.setShippingTotal();
        this.setOrderTotal();   
        this.setTaxTotal(); 
        if(IS_EU){
          this.setVATDiscount();
        }
        if(IS_JAPAN){
          this.setCODTotal();
        }
      }
        
    },
    watchSurchageInfo: function(){
      $('#surchage_info').click(function(e){
        $('#surchage_info_tooltip').remove()
        $('body').append('<div id="surchage_info_tooltip">Canadian Surcharge covers all Goods and Services Tax (GST), Harmonized Sales Tax (HST) as well as Duty and Brokerage.<br><br>Canadian customers will not incur any additional charges upon delivery.<br /><span style="display:block;text-align:center;font-weight:bold;margin:10px 0 5px 0;"><span style="border:1px solid #CCC;padding:2px 10px">OK</span></span></div>');
        $('#surchage_info_tooltip').css({position: 'absolute', top: $('#surchage_info').offset().top - 20}).show()
        setTimeout(function(){
          $('#surchage_info_tooltip').css('opacity', 1);
          $('html').bind('click.surchargeClear', function(){
            $('#surchage_info_tooltip').remove();
            $('html').unbind('click.surchargeClear')
          });
        }, 10);
        e.preventDefault();
      });

    },
    setupInlineValidation: function(){
      $('form', this.el).isHappy({
          selectorScope: this.el, // mod to happy.js so we can scope our fields to this.el.
          fields: {
            '#order_billing_name': {
              required: true,
              message: 'first & last name required',
              test: function(val){
                return FIRST_AND_LAST_NAME_FORMAT.test(val)
              }
            },
            '#order_tel': {
              required: true,
              message: '10 digit number required',
              test: function(val){
                return TEL_FORMAT.test(val.replace(/-|\(|\)|\s/g, '')) // strip out parenthesis and dashes
              }
            },        
            '#order_billing_zip, #obz': {
              required: true,
              message: '', // Lost the message, we'll just highlight it.
              test: function(val){
                if($("#order_billing_country").val() == 'CANADA'){
                  return CANADA_ZIP.test(val.toUpperCase());
                 } else {
                   return US_ZIP.test(val);
                 }
              }

            },
            '#order_email': {
              required: true,
              message: 'invalid email',
              test: function(val){
                return EMAIL_FORMAT.test(val);
              }
            },
            '#order_billing_address': {
              required: true,
              message: 'required'
            },
            '#order_billing_city': {
              required: true,
              message: 'required'
            },
            '#order_terms': {
              required: true,
              message: 'terms must be accepted',
              test: function(val){
                $('#order_terms', this.el).prop('checked');
              },
              errorPosition: {placement: 'append', selector: '#order-terms-label'}
            },
            '#order_billing_state': {
              required: true,
              message: 'required'
            },
            '#credit_card_n': {
              required: true,
              message: 'required'
            },
            '#cvv-container input': {
              required: true,
              message: ''

            }
          }
        });
    }
  });
});
$(document).ready(function() {
  ConfirmationItemViewTemplate = Backbone.View.extend({
    tagName: 'tr',
    template: _.template($('#confirmationItemViewTemplate').html()),
    events: {
      'click td.cart-image img': 'jumpToProduct'
    },
    jumpToProduct: function(e){
      Supreme.app.navigate("products/" + this.model.product_id + '/' + this.model.style_id, {trigger: true});      
    },
    render: function(){
      $(this.el).html($(this.template(this.model)));
      return this;
    }
  });  
});
$(document).ready(function() {
  LookbookItemView = Backbone.View.extend({
    template: _.template($('#lookbookItemViewTemplate').html()),
    events: {
      'click .lookbook-item': 'zoom'
    },
    initialize: function(){
      var self = this;

      this._isZoomed  = false;

      // Set up the following functions here so that I can remove them from the dom elements on zoom close.
      self.navClose = function(e) {
        e.preventDefault();
        e.stopImmediatePropagation();

        var killZoomFragment = Backbone.history.getFragment().replace('/zoom', '');
            Supreme.app.navigate(killZoomFragment, {trigger: false, replace: true});

        self.killZoom();
      };

      self.wrapperClose = function(e) {

        var killZoomFragment = Backbone.history.getFragment().replace('/zoom', '');
            Supreme.app.navigate(killZoomFragment, {trigger: false, replace: true});

        self.killZoom();
      }

      self.handleHash = function(e) {
        // If moving from zoom state URL to non zoom state URL - kill the zoom (for back buttons).
        if ((e.oldURL.indexOf('zoom') > -1) && (e.newURL.indexOf('zoom') <= -1)) {
          self.killZoom();
        }
      }
    },
    render: function(name){
      console.log(1);
      this.model.stripSomeMarkupFromCaption();
      var json = this.model.toJSON();
      $(this.el).html(this.template(json));

      return this;
    },
    zoom: function(e){
      if(this._isZoomed){
        return false;
      }

      $('html').addClass('is-zoomed');

      if(_isLookbookSwiping){ // No zoom while swiping, otherwise we might zoom the wrong thing.
        return;
      }
      // if(iPad){return;} // No zoom for iPad.

      var self = this;
      // If they click into the categories from the lookbook make sure to close the lookbook.
      // $('#categories-link').on('click.lookbook-zoom', function(e){
      //   self.killZoom();
      // });

      // The image starts with the current product image, sized way up.
      var img = new Image();
      $(img).attr({src: self.model.get('medium'), width:'862', height:'1248'});
      $(img).css({width: '862px', height:'1248px'});

      self.img = img;


      var zoomWrapper = $('<div id="lookbook-zoom-wrapper"><div id="lookbook-scroller"></div></div>');
      $('#lookbook-scroller', zoomWrapper).append($(img));
      zoomWrapper.css('top', $(window).scrollTop() + 'px');

      // iphone only, was causing some scrolling glitches on the test android. not letting zoomed image scroll down.
      if(iPhone){
        zoomWrapper.css({height: window.screen.availHeight  });
      }

      $('#container').before(zoomWrapper);

      zoomWrapper.css({opacity: 1});

      self.scroller = new IScroll('#lookbook-zoom-wrapper', {
        zoom: true,
        tap: true,
        hideScrollbar: true,
        scrollX: true,
        scrollY: true,
        zoomMax: 2
      });

      // Need to convert the point clicked (available in offsetX and offsetY)
      // to the point we want to zoom in on on the image.
      // not ipad.
      if(!iPad){
        var scrollLeft = (e.offsetX/335 * 862) - zoomWrapper.width()/2;
        var scrollTop = (e.offsetY/485 * 1248) - zoomWrapper.height()/2;
        if(scrollTop <= 0){
          scrollTop = 0;
        }

        if(scrollTop > zoomWrapper.height()){
          scrollTop = zoomWrapper.height(); // deal with an issue of zooming in too low
        }
        self.scroller.scrollTo(-scrollLeft, -scrollTop, 0);
      }

      // window.scroll(0, 0);
      $(img).bind('load', function() {    // when image has loaded...

       }).attr({
         src: self.model.get('url'),
         width: 862,
         height: 1248
       });

        if (!android) {
          $(img).on('click', self.wrapperClose);
        } else {
          $(img).on('tap', self.wrapperClose);
        }

        $('.supreme-navigation').on('click', self.navClose);

        $(window).on('hashchange', self.handleHash);

        var zoomFragment = Backbone.history.getFragment() + '/zoom';
        Supreme.app.navigate(zoomFragment, {trigger: false});

       self._isZoomed = true;

    },
    killZoom: function(){
      $('#categories-link').off('click.lookbook-zoom');
        var self = this;

        if(!this._isZoomed){return;}
        window.scroll(0, 0);
          this.scroller.destroy();
          if (!android) {
            $(self.img).off('click', self.wrapperClose);
          } else {
            $(self.img).off('tap', self.wrapperClose);
          }
          $('.supreme-navigation').off('click', self.navClose);
          $(window).off('hashchange', self.handleHash);

          self._isZoomed = false;
          $('html').removeClass('is-zoomed');

          $('#lookbook-zoom-wrapper').animate({opacity: 0}, fadeSpeed, fadeEasingType, function(){
            $('#lookbook-zoom-wrapper').remove();
          });
      }

  });
});
$(document).ready(function() {
  LookbookView = Backbone.View.extend({
    template: _.template($('#lookbookViewTemplate').html()),

    render: function(name){
      // Hide the footer to begin with, to prevent some jumpiness.
      // We show it again after stuff loads in.
      $('footer').hide();

      var self = this;
      this.collection.fetch({
        success: function(){
          $(self.el).html(self.template);
          // When the collection is done loading we'll show it.
          _.each(self.collection.models, function(i){
            var lookbookItemView = new LookbookItemView({model: i, collection: self.collection});
            $('.swipe-wrap', self.el).append(lookbookItemView.render().el);
          });

          // After the load we can show the footer again.
          setTimeout(function(){
            $('footer').show();
          }, 100);

          window.lookbookSwiper = Swipe(document.getElementById('lookbook-items'), {
            continuous: false,
            transitionEnd: function(index, elem){
              _isLookbookSwiping = false;
            },
            callback: function(){
              _isLookbookSwiping = true;
              self.updateCaption();
              ga_track('pageview');
            }
          });
          self.updateCaption();
        }
      });
    },
    updateCaption: function(){
      $('#lookbook-pos', this.el).html((window.lookbookSwiper.getPos() + 1)+ '/' + this.collection.length);
      $('#lookbook-title', this.el).html(this.collection.title);
      $('#lookbook-item-caption', this.el).html(this.collection.at(window.lookbookSwiper.getPos()).get('caption'));
    }
  });
});
$(document).ready(function() {
  // Show the order confirmation and all the associated data.
  // Assumes the model is a subset of all the order data needed for this sort of thing.
  OrderConfirmationView = Backbone.View.extend({
    tagName: 'div',
    template:_.template($('#orderConfirmationTemplate').html()),
    initialize: function() {
      // Make back button go home.
      $('html').removeClass('activate-back');
    },
    render: function(){
      $(this.el).html(this.template(this.model)); 
      var currency = this.model['currency'];   
      var tBody = $('<tbody>');
      _.each(this.model.purchases, function(p){
        p['currency'] = currency;
        var itemView = new ConfirmationItemViewTemplate({model: p});
        tBody.append(itemView.render().el);
      });
      $('table tbody', this.el).replaceWith(tBody);

      // If there's a COD in the order conf and it's true we'll show that line,
      // otherwise it's hidden.
      if(!_.isUndefined(this.model['cod']) && this.model['cod'] ){
        $('#cod_row', this.el).show();
      }
      if(!_.isUndefined(this.model['discount_total']) && this.model['discount_total'] ){
        $('#discount_row', this.el).show();
      }

      if(!_.isUndefined(this.model['manual_review']) && this.model['manual_review'] ){
        $('#manual_checkout_copy', this.el).show();
        $('#standard_checkout_copy', this.el).hide();
        $('#cart-items', this.el).hide();
        $('#totals', this.el).hide();
      } else {
        $('#manual_checkout_copy', this.el).hide();
        $('#standard_checkout_copy', this.el).show();
      }

      $('#join_mailinglist').change(function(e){
        var commit = $(e.target).attr('checked') ? 'subscribe' : 'unsubscribe';
        var data = {
          commit: commit
        };
        if(IS_EU){
          data.eu_order_mailing_list = 1;
        }
        var url = 'http://' + document.domain + '/order_mailinglist';
        $.post(url, data);
        e.preventDefault();
      });

      return this;
    }
  });
});
$(document).ready(function() {
  // Product detail view. Renders the product, the style, style selector, and the cart widgets.
  ProductDetailView = Backbone.View.extend({
    template:_.template($('#productDetailTemplate').html()),
    styleDetailTemplate:_.template(styleDetailTemplate),
    styleSelectorView: null,
    events: {
      'click #style-image-container img': 'zoom',
      'touchstart #size-options-link': 'sizeOptionsTap',
      'touchstart #qty-options-link': 'qtyOptionsTap',
      'touchend #size-options-link': 'sizeOptionsTapEnd',
      'touchend #qty-options-link': 'qtyOptionsTapEnd',
      'change #size-options': 'sizeOptionsChanged',
      'change #qty-options': 'qtyOptionsChanged'
    },
    initialize: function(){
      var self = this;

      this.$window = $(window);
      this._isZoomed = false;
      // Be aware of changes to the product's selected style so we can change stuff up.
      this.render = _.bind(this.render, this);
      this.renderWidgets = _.bind(this.renderWidgets, this);
      this.renderStyleDetail = _.bind(this.renderStyleDetail, this);
      this.renderStyleSpecifics = _.bind(this.renderStyleSpecifics, this);
      this.model.bind('change:initialPhotoIndex', this.renderWidgets);
      this.model.bind('change:initialPhotoIndex', this.renderStyleDetail);
      this.model.bind('change:selectedStyle', this.renderStyleSpecifics);

      Supreme.app.cart.bind("itemAdded", this.renderWidgets);

      // Set up the following functions here so that I can remove them from the dom elements on zoom close.
      this.navClose = function(e) {
        var killZoomFragment = Backbone.history.getFragment().replace('/zoom', '');
            Supreme.app.navigate(killZoomFragment, {trigger: false, replace: true});

        e.preventDefault();
        e.stopImmediatePropagation();
      };

      this.wrapperClose = function(e) {
        var killZoomFragment = Backbone.history.getFragment().replace('/zoom', '');
            Supreme.app.navigate(killZoomFragment, {trigger: false, replace: true});
      }

      this.handleHash = function(e) {
        // If moving from zoom state URL to non zoom state URL - kill the zoom (for back buttons).
        if ((e.oldURL.indexOf('zoom') > -1) && (e.newURL.indexOf('zoom') <= -1)) {
          self.killZoom();
        }
      }

      this.$window.bind('kill-zoom', function(){ 
        self.killZoom();
      });

      this.$window.bind('start-zoom', function(e){    
        self.zoom(e);    
      });

      // We'll start loading the swatch images right now.
      this.model.get('styles').each(function(style){
        prefetchImage(style.get('swatch_url'));
      });

    },
    render: function(){
      $(this.el).empty();
      if(Backbone.history.fragment == "cart"){
        return;
      }

      var json = this.model.toJSON();

      $(this.el).html(this.template(json));
      this.renderStyleSpecifics(true);
      $('footer').css({
        position: 'relative',
        bottom: 'auto',
        left: 'auto',
        right: 'auto'
      });
      
      $('#keep-shopping', this.el).click(function(e){
        e.preventDefault(); // Don't jump up on click.
        Supreme.app.navigate("#categories", {trigger: true});
      });
      $('#itunes_link').click(function() {window.open($(this).attr('href'), 'itunes_store')});
      mixpanelTrack('Product View', {Category: _currentCategoryPlural, "Product Color": json.selectedStyle.get('name'), 'Product Number': json.ino, "Product Name": json.name, "Product Cost": formatCurrency(this.model.actualPrice()), "Device Type": "Mobile"})      

      return this;
    },
    renderStyleSpecifics: function(forceRenderStyleDetail){
      this.renderStyleDetail(forceRenderStyleDetail);
      this.renderWidgets();
    },
    renderWidgets: function(){

      // Sometimes it might be possible for the widgets to render, on cart change, for the wrong element.
      var productIdFromUrl = Backbone.history.fragment.split('/')
      productIdFromUrl = productIdFromUrl[1];
      // Let's do a sanity check before we re-render, to make sure we're not rendering for the wrong thing.
      if(parseInt(productIdFromUrl) != this.model.get('id')){
        return;
      }

      var productWidgetsView = new ProductWidgetsView({model: this.model});
      $('#product-widgets', this.el).html(productWidgetsView.render().el);

      // Add in the Add to Cart button.
      this.addToCartButton = new AddToCartButtonView({model: this.model}); // pass in the product
      this.sizeOptionsChanged();      
      this.qtyOptionsChanged();
      // Are all the sizes sold out? If so, mark the button as disabled.
      if(this.model.get('selectedStyle').get('sizes').all(function(s){
        return s.get('stock_level') == 0;
      })){
        // Hide the drop down.
        this.addToCartButton.soldOut();
      };

      // Drop in the styles.
      var styleSelectorView = new StyleSelectorView({
        el: $('#styles', this.el),
        model: this.model
      }).render();

      if(this.model.has('selectedStyle')){
        this.highlightCurrent();
      }

        var isStyleInCart = Supreme.app.cart.hasStyle(this.model.get('selectedStyle'));
        var canAddStyle   =   Supreme.app.cart.canAddStyle(this.model.get('selectedStyle'));

        if(isStyleInCart){
          $('#in-cart', this.el).show();
          $('#size-options-link', this.el).hide();
          $('#qty-options-link', this.el).hide();
        } else {
          if(canAddStyle){
            $('#in-cart', this.el).hide();
            // IS it sold out?
            if(this.model.get('selectedStyle').isSoldOut()){
              $('#size-options-link', this.el).hide();
              $('#qty-options-link', this.el).hide();
            } else {
              $('#size-options-link', this.el).show();
              $('#qty-options-link', this.el).show();
            }

          } else {
            $('#qty-options-link', this.el).hide();
            // Not in cart, can't add it? Means the other style is in there already.
            $('#cart-warning', this.el).remove();

            // Types of errors - either it's the standard, only 1 of a style in cart is allowed, or it's the bit where more than 1 style per product is allowed, within a limit.
            if(this.model.get('can_buy_multiple_with_limit') > 1){
              $('#product-widgets', this.el).append($('<p id="cart-warning" class="warning"><span>' + LANG.limited_with_count + '</span></p>'));
            } else {
              $('#product-widgets', this.el).append($('<p id="cart-warning" class="warning"><span>' + LANG.limited + '</span></p>'));
            }
            
            $('#widgets-container', this.el).hide();
          }
        }


        if(this.model.get('cod_blocked')) {
          $('#cod_blocked_product_view', this.el).show();
        }

        // If it's just n/a and there's only 1 size don't show it.

        if(this.model.get('selectedStyle').get('sizes').models.length == 1 &&
         this.model.get('selectedStyle').get('sizes').first().get('name') == 'N/A'){
           $('#size-options-link', this.el).hide();
           $('#size-options', this.el).hide(); // Don't want to be able to hit touch on the Select.
         }
         $('#cart-update', this.el).empty();
        $('#cart-update', this.el).append(this.addToCartButton.render().el);

    
        if($('#size-options option', this.el).length <= 1){
          $('#size-options-link', this.el).removeClass('enabled');          
        } else {
          $('#size-options-link', this.el).addClass('enabled');
        }

        if($('#qty-options option', this.el).length <= 1){
          $('#qty-options-link', this.el).removeClass('enabled');          
        } else {
          $('#qty-options-link', this.el).addClass('enabled');
        }        

        var nextProduct = getNextProductFromId(this.model.get('id'));
        // Is the next thing the same as the current thing? Don't show the item.
        if(nextProduct.id == this.model.get('id')){
          $('#next', this.el).hide();
        } else {
          $('#next', this.el).show();
          $('#next', this.el).attr('href', '#products/' + nextProduct.id);
          $('#next span', this.el).html(_currentCategory);
          $('#next', this.el).click(function(e){
            setTimeout(function(){
              window.location.href = '#products/' + nextProduct.id;
            }, 140);
            $.scrollTo(0, 130);
            e.preventDefault();
          });
        }
        setTimeout(function(){
          $('#product-widgets', this.el).css('opacity', 1);
          $('#product-details-content', this.el).css('opacity', 1);
          $('#product-nav', this.el).css('opacity', 1);
        }, 100);
        
    },
    // Highlights the currently selected style in the style selector group.
    highlightCurrent: function(){
      $('#style-selector li div img', this.el).removeClass("selected");
      // Highlight the std style or an alt?
      var initialIdx = this.model.get('selectedStyle').get('initialPhotoIndex');
      if(initialIdx == 0){
        $("#style-" + this.model.get('selectedStyle').get('id') + ' img.style-thumb', this.el).addClass("selected");
      } else {
        $("#style-" + this.model.get('selectedStyle').get('id') + ' img[altidx="' + initialIdx + '"]', this.el).addClass("selected");
      }

    },
    // Drop in the first style
    renderStyleDetail: function(forceStyleImageRender){
      var self = this;
      // Don't need to actually refresh this unless the product ID is different.
      // Or we're forcing the render, as we do when we're showing a product anew.
      // This second part is because hitting the back button between styles was causing this not to re-render.
      if(forceStyleImageRender === true || parseInt($('#product').attr('data-product-id')) != this.model.get('id')){
        $('#style-image', this.el).html(this.styleDetailTemplate(this.model.get('selectedStyle').toJSON()));

      $('#zoom-close').click(function(e){
        self.killZoom();
      });

      
      var imageElements = '';
      self.model.get('styles').each(function(style) {
        var img = new Image()
        $(img).attr({
            width: (iPad ? 600 : (isHiResAndWide()  ? 300 : 250) ),
            height: (iPad ? 600 : (isHiResAndWide() ? 300 : 250))
        }).css({
          visibility: 'hidden' // making them invisible allows their spinners to show, until they load in.
        }).bind('load', function(){
          $(this).css({visibility: 'visible'});
        });

        // This madness forces the load event if it doesn't get called but it's complete.
        // Used to deal with the fact that an already loaded image won't call its callback otherwise
        if ($(img).attr('complete') || $(img).attr('complete') === undefined){ $(img).trigger('load'); }

        var div = $('<div class="swiper-image-container">');
        var newImage = $(img).attr('src', (iPad ? style.zoomedPhoto() : style.productPhoto()));
        div.append(img);
        imageElements += div[0].outerHTML;
      });

      $('#style-image-container', self.el).find('.swipe-wrap').html(imageElements);

      } else {
        // Just changing style?
        window.productSwiper.slide(self.model.get('styles').indexOf(self.model.get('selectedStyle')), 1)
      }

      // Did we change the image to an alt style?

      var newIndex = self.model.get('styles').indexOf(self.model.get('selectedStyle'));
      var imageAtNewPosition = $('#style-image-container', self.el).find('.swipe-wrap > div').get(newIndex).children[0];
      var imgUrlAtNewPosition = $('#style-image-container', self.el).find('.swipe-wrap > div').get(newIndex).children[0].src;

      if(imgUrlAtNewPosition != self.model.get('selectedStyle').productPhoto()){
        $(imageAtNewPosition).unbind('load').css('visibility', 'hidden');
        $(imageAtNewPosition).bind('load', function() {
          $(this).css({visibility: 'visible'});
        });
        if(iPad){
          imageAtNewPosition.src = self.model.get('selectedStyle').zoomedPhoto();
        } else {
          imageAtNewPosition.src = self.model.get('selectedStyle').productPhoto();
        }

        if ($(imageAtNewPosition).attr('complete') || $(imageAtNewPosition).attr('complete') === undefined){ $(imageAtNewPosition).trigger('load'); }

      }
      self.killZoom();

      // Update the field names.
      $('#style-name', this.el).html(self.model.get('selectedStyle').get('name'));
      $('#name', this.el).html(self.model.get('name'));
      $('#product', this.el).attr('data-product-id', self.model.get('id'));

      if (self.model.get('selectedStyle').get('description') && self.model.get('selectedStyle').get('description').length > 0) 
        $('#description').text(self.model.get('selectedStyle').get('description'));


      $('#style-image-container').bind('touchmove', function(){
        _isSwiping = true;
        setTimeout(function(){
          // fallback in case for some reason the transition doesn't act like it should, and _isSwiping is never set to false properly.
          _isSwiping = false;
        }, 1000);
      });

      

      this.highlightCurrent();
      return this;
    },
    sizeOptionsChanged: function(){
      var val = $('#size-options', this.el).val();
      val = $("#size-options option[value='" + val + "']", this.el).text()
      $('#size-options-link', this.el).text(val);
    },
    qtyOptionsChanged: function(){
      var val = $('#qty-options', this.el).val();
      val = $("#qty-options option[value='" + val + "']", this.el).text()
      $('#qty-options-link', this.el).text(val);
    },    
    sizeOptionsTap: function(e){
      e.preventDefault();
      e.stopImmediatePropagation();
      if($('#size-options option').length > 1){
        $(this).addClass('touching');        
        setTimeout(function(){
          openSelect('#size-options');                
        }, 10);
        
      }
      
    },
    qtyOptionsTap: function(e){
      e.preventDefault();
      e.stopImmediatePropagation();
      if($('#qty-options option').length > 1){
        $(this).addClass('touching');        
        setTimeout(function(){
          openSelect('#qty-options');          
        }, 10);
      }      
    },
    sizeOptionsTapEnd: function(e){
      e.preventDefault();
      e.stopImmediatePropagation();
      $(this).removeClass('touching');            
    },
    qtyOptionsTapEnd: function(e){
      e.preventDefault();
      e.stopImmediatePropagation();
      $(this).removeClass('touching');      
    },
    updateUrl: function(){
      // Update the "URL", to allow for direct linking to this style.
      // Only do this if we'fe navigated to this product on our own
      var frag = "products/" + this.model.get('id') + "/" + this.model.get('selectedStyle').get('id');
      Supreme.app.navigate(frag, {trigger: false});
      // Manually set the last fragment since we don't have a true route.
      setLastVisitedFragment(frag);
      _gaq.push(['_trackPageview', '/mobile/' + frag]);
    },

   zoom: function(e){
      $('html').addClass('is-zoomed');

      var isPinchZoom = typeof(e.type) != 'undefined' && e.type == 'start-zoom';

      if(_isSwiping && !isPinchZoom){ // No zoom while swiping, otherwise we might zoom the wrong thing.
        return;
      }
      if(iPad){return;} // No zoom for iPad.
      var self = this;
      _gaq.push(['_trackEvent', "products", "zoom", "Product ID " + self.model.get('id')]);
      var current = Backbone.history.fragment.split('/')[1];
      if(current != self.model.get('id')){
        return;
      }
      self.finishZoomBits(e);
    },
    finishZoomBits: function(e){
        var self = this;
        // The image starts with the current product image, sized way up.
        var img = new Image();
        $(img).attr({src: self.model.get('selectedStyle').productPhoto(), width:'600', height:'600'});
        $(img).css({width: '600px', height:'600px'})

        // full screen?
        if(window.navigator.standalone){
          $(img).addClass('big-screen');
        }
        if($(window).height() >= 548 ){
          $(img).addClass('app-screen');
        }

        var w = 600;

        // If they click into the categories from the lookbook make sure to close the lookbook.
        if (!android) {
          $('#product-zoom-wrapper').on('click', self.wrapperClose);
        } else {
          $('#product-zoom-wrapper').on('tap', self.wrapperClose);
        }

        $('.supreme-navigation').on('click.product-zoom', self.navClose);

        $('#product-zoom-scroller').html($(img));
        $('#product-zoom-wrapper').show().animate({opacity: 1}, fadeSpeed, fadeEasingType);
        scroller = new IScroll('#product-zoom-scroller', {
          zoom: true,
          hideScrollbar:true,
          tap: true,
          click: true,
          scrollX: true,
          scrollY: true,
          zoomMax: 1.2,
          zoomMin: 0.8,
          startZoom: (isHiResAndWide() ? 1 : 0.8),
          directionLockThreshold: 20
         });

         if(window.orientation == 90 || window.orientation == -90){
            if(window.navigator.standalone || $(window).width() >= 568 ){
              if($(window).width() >= 736){
                scroller.scrollTo(-35, -45, 0);  // iphone6+
              } else if($(window).width() >= 667){
                scroller.scrollTo(-60, -45, 0);  // iphone6
              } else {
                scroller.scrollTo(-130, -45, 0);  /// landscape
              }
            } else {
              scroller.scrollTo(-90, -45, 0);  /// landscape
            }
         } else {
           // full screen?
           if(window.navigator.standalone || $(window).height() >= 548 ){
            if($(window).width() >= 414){
              scroller.scrollTo(-115, -20, 0);  // iphone6+
            } else if($(window).width() >= 375){
              scroller.scrollTo(-140, -40, 0);  // iphone 6
            } else {
              scroller.scrollTo(-105, -9, 0);  // portait
            }
           } else {
             scroller.scrollTo(-105, -25, 0);  // portait
           }
         }

        // We have a rudimentary download speed test.
        // If it looks like zoomed images are downloading too slow, we'll use lower res images.

        var downloadSpeedMedian = 0;
        var useLowerResZoomImage = false;
        if(_.keys(_zoomedImageDownloadSpeeds).length > 3){ // say we need a sample size of this many to consider the speeds.
          // What's the median?
          var downloadSpeedMedian = median(_.values(_zoomedImageDownloadSpeeds));
          if(downloadSpeedMedian > 1000){ // milliseconds!
            useLowerResZoomImage = true;
          }
        }


         var downloadStart = new Date().getTime();
         var zoomedImageUrl = self.model.get('selectedStyle').zoomedPhoto(useLowerResZoomImage);
         $(img).bind('load', function() {    // when image has loaded...

            var downloadStop = new Date().getTime();

            if(_.isUndefined(_zoomedImageDownloadSpeeds[zoomedImageUrl])){
              _zoomedImageDownloadSpeeds[zoomedImageUrl] = downloadStop - downloadStart;
              _zoomedImageLoadOrder.push(zoomedImageUrl);
              // Too many loaded now? Drop one.
              if(_zoomedImageLoadOrder.length > 5){
                var droppedUrl = _zoomedImageLoadOrder.shift();
                // Make sure we take it out of the hash too.
                delete(_zoomedImageDownloadSpeeds[droppedUrl]);
              }
            }

          }).attr({
            src: zoomedImageUrl,
            width: w,
            height: w
          });

          var zoomFragment = Backbone.history.getFragment() + '/zoom';
          Supreme.app.navigate(zoomFragment, {trigger: false});

          self.$window.on('hashchange', self.handleHash);

          self._isZoomed = true;

    },
    killZoom: function(){
      if(!this._isZoomed){return;}
      $('html').removeClass('is-zoomed');

      // Remove the click functions so they don't get added to elements multiple times.
      $('.supreme-navigation').off('click.product-zoom', this.navClose);
      if (!android) {
        $('#product-zoom-wrapper').off('click', this.wrapperClose);
      } else {
        $('#product-zoom-wrapper').off('tap', this.wrapperClose);
      }
      this.$window.off('hashchange', this.handleHash);
      var self = this;
      $('#product-zoom-wrapper').animate({opacity: 0, duration: fadeSpeed});
      setTimeout(function(){
        $('#product-zoom-wrapper').hide();
        scroller.destroy();
        $('#product-zoom-scroller').html("");
        popZoomTriggered = false;
        self._isZoomed = false;
      }, fadeSpeed - 500);
    }


  });
});

var openSelect = function(selector){
     var element = $(selector)[0], worked = false;
    if (document.createEvent) { // all browsers
        var e = document.createEvent("MouseEvents");
        e.initMouseEvent("mousedown", true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
        worked = element.dispatchEvent(e);
    } else if (element.fireEvent) { // ie
        worked = element.fireEvent("onmousedown");
    }
}
;
$(document).ready(function() {
  // Product list view, after drilling down into a category.
  ProductListView = Backbone.View.extend({
    tagName: 'li',
    className: 'selectable',    
    template:_.template(categoryProductListItemView),
    events: {
      click: 'select'
    },
    render: function(){
      $(this.el).html(this.template(this.model.toJSON()));
      return this;
    },
    select: function(){
      Supreme.app.navigate("products/" + this.model.get('id'), {trigger: true});      
    }
  });
  
});
$(document).ready(function() {
  ProductWidgetsView = Backbone.View.extend({
    template:_.template($('#productWidgetsTemplate').html()),
    tagName: 'div',
    id: 'widgets-container',
    initialize: function(){
      this.render = _.bind(this.render, this);
      Supreme.app.cart.bind("itemAdded", this.render);   
    },
    render: function(){
      var productData = this.model.toJSON();
      var sizeForStyleInCart = Supreme.app.cart.getSizeForStyle(this.model.get('selectedStyle'));
      // Pass in the size selected for this style, if it's in the cart.
      _.extend(productData, {sizeForStyleInCart: sizeForStyleInCart}); 
      $(this.el).html(this.template(productData));
      return this;
    }
  });
  
});
$(document).ready(function() {
  StaticContentView = Backbone.View.extend({
    // Given a few names of static pages (terms, sizes, etc),
    // loads that content.
    template: _.template($('#staticViewTemplate').html()),
    initialize: function(){
      var self = this;

      self.closeWithBackButton = function(e) {
        self.close();
        e.preventDefault();
        e.stopImmediatePropagation();
      };

      self.handleHash = function(e) {
        // If moving from zoom state URL to non zoom state URL - kill the zoom (for back buttons).
        self.close();
        return false;
      }

      $(window).on('hashchange', self.handleHash);

      $('.supreme-navigation').on('click', self.closeWithBackButton);
    },
    close: function(){
      var self = this;
      $('html').removeClass('static-view');
      $(window).off('hashchange', self.handleHash);
      $('.supreme-navigation').off('click', self.closeWithBackButton);
      // $.scrollTo(0, scrollSpeed, function(){
        $('#static-view').animate({opacity: 0}, 0, fadeEasingType, function(){         
          $('#static-view').remove();
          $('#static-loading').remove();
          $('.static.close').remove();
          $('footer').css({visibility:'visible'});
        });
      // });
    },
    render: function(name){
      var self = this;
      var url = '/mobile/static/' + name;

      // $('header').bind('click', function(){
      //   self.close();
      // });

      var loading = $('<div id="static-loading"></div>');
      
      $('footer').css({visibility:'hidden'});
      
      loading.css({
        width: $('body').width(),
        height: $('body').height() + $('header').height(),
        position: 'absolute',
        top: $('header').offset().top + $('header').height(),
        left: 0,
        background: '#F4F4F4',
        zIndex: 1999
      });

      $('body').prepend(loading);
      
      $.get(url, function(content){
        var html = $(self.template());
        $('#static-content', html).html(content);
        $('#main').before(html);
        $('#static-view').animate({opacity: 1}, 0, fadeEasingType, function(){ 
          loading.bind('click', function(){
            self.close();
          });
          
          $('p.close span', this.el).bind('click', function(){
            self.close();
          });
        });
      });      
    }
  });
});
$(document).ready(function() {
  StyleSelectorOptionView = Backbone.View.extend({
    tagName: 'li',
    template:_.template($('#styleSelectorOptionTemplate').html()),
    
    events: {
      'click img': 'select'
    },
    render: function(){
      $(this.el).html(this.template(this.model.toJSON()));
      return this;
    },
    select: function(e){      
      var styleId = $(e.target).parent().parent().attr('id').split('-')[1];

      // Set the product's selected style to it.
      // This will trigger an even that will update the DOM and do some other stuff.

      var altIdx;
      // Show the alt image if necessary.
      if($(e.target).hasClass('alternate')){
        altIdx = parseInt($(e.target).attr('altidx'));
        // this.model.get('product').set('selectedStyleAlt', altIdx);
      } else {
        altIdx = 0;
      }

      // Changing style?
      if(parseInt(styleId) != parseInt(this.model.get('product').get('selectedStyle').get('id'))){
        var newStyle = this.model.get('product').get('styles').get(styleId);
        newStyle.set('initialPhotoIndex', altIdx);
        this.model.get('product').set('selectedStyle', newStyle);  
      } else { // Not changing style?
        this.model.get('product').get('selectedStyle').set('initialPhotoIndex', altIdx);
        var currentTime = new Date().getTime();        
        this.model.get('product').set('initialPhotoIndex', currentTime);
      }



      
      var frag = "products/" + this.model.get('product').get('id') + "/" + this.model.get('product').get('styles').get(styleId).get('id');
      
      Supreme.app.navigate(frag, {trigger: false});     
      
      // Manually set the last fragment since we don't have a true route.
      setLastVisitedFragment(frag);
      _gaq.push(['_trackPageview', '/mobile/' + frag]);

      var currency;
      if (IS_JAPAN)
        currency = 'JPY'
      else if (IS_EU)
        currency = LANG.currency == "eur" ? 'EUR' : 'GBP'
      else
        currency = 'USD'

      var price = $('.price').text().replace(/[^\d\.]/,'')


      mixpanelTrack('Product View', {Category: _currentCategoryPlural.toLocaleLowerCase(), "Product Color": this.model.get('product').get('selectedStyle').get('name'), "Product Name": this.model.get('product').get('name'), "Product Cost": price, 'Currency': currency, "Device Type": "Mobile"})      


      
      return false; 
    }    
  });
});
$(document).ready(function() {
  // Renders the widgets to choose the current style.
  // Bound to the product detail view, so it can tell it when stuff happens.
  StyleSelectorView = Backbone.View.extend({
    template:_.template($('#styleSelectorTemplate').html()),
    initialize: function(){
      var self = this;
      this._styleSelectorOptionViews = [];
      
      this.model.get('styles').each(function(style){
        // TODO: Skip any style that doesn't have sizes?
        self._styleSelectorOptionViews.push(new StyleSelectorOptionView({model:style, product: self.model, id: 'style-' + style.get('id')}));
      });      

    },
    render: function(){
      var self = this;
      $(this.el).html(this.template(this.model.toJSON()));      
      var styleSelector = $('#style-selector', self.el);
      _(this._styleSelectorOptionViews).each(function(styleSelectorOptionView){
        styleSelector.append(styleSelectorOptionView.render().el);
      });  
      
      // Would really rather not center this stuff this way, but thems the breaks.
      // var newWidth = this._styleSelectorOptionViews.length * 36 + (this._styleSelectorOptionViews.length - 1) * 5;
      // if(newWidth > $('#container').width()){
      //   // The 8th shouldn't have right margin, since we want to wrap there.
      //   newWidth = $('#container').width() - 20;
      // }
      
      var lis = styleSelector.find('li');
      if(lis.length > 8){
        styleSelector.addClass('wide');
      }

      // Would really rather not center this stuff this way, but thems the breaks.
      // var newWidth = this._styleSelectorOptionViews.length * 36 + (this._styleSelectorOptionViews.length - 1) * 5;
      // if(newWidth > $('#container').width()){
      //   // The 8th shouldn't have right margin, since we want to wrap there.
      //   newWidth = $('#container').width() - 20;
      // }
      

 
      // styleSelector.css({width: newWidth});

      return this;      
   
    }
 
  });
  
});
function defaultRoute(){
  if($('body').hasClass('for-native-checkout')){
    return "checkout";
  } else {
    return "categories";
  }
}

var ptr = false;

$(document).ready(function(){
  // Cache the $('#main') selector for speed.
  var $main = $('#main');
  // Function that makes sure opacity is 1: If not, fade in again.
  function confirmMainOpacity() {
    setTimeout(function() {
      if ($main.css('opacity') < 1) {
        $main.animate({opacity: 1}, fadeSpeed, fadeEasingType);
      }
    }, 50);
  }
  /* Router */
  AppRouter = Backbone.Router.extend({
    routes: {
      "":                               defaultRoute(),
      "categories":                     "categories",
      "categories/*name":               "categoryProductList",  // category list view.
      "products/:id":                   "productDetail",
      "products/:id/*styleId":          "productDetail", // optional way of jumping directly to style.
      'cart':                           "cart",
      'checkout':                       "checkout",
      'chargeError':                    "chargeError",
      'chargeErrorBot':                 "chargeErrorBot",
      'confirmOrder':                   "confirmOrder",
      'paypalConfirmOrder':             "paypalConfirmOrder", // Where we send paypal confirmation users.
      'lookbook':                       "lookbook",
      'lookbook/zoom':                  "lookbook"
    },

    lookbook: function(){
      if(goLastPlace(Supreme.app)){return false; };
      if (Backbone.history.getFragment().indexOf('zoom') > -1) {
        var redirectFragment = Backbone.history.getFragment().replace('/zoom', '');
        Supreme.app.navigate(redirectFragment, {trigger: true, replace: true});
      }
      showCartAndCheckout();
      // TODO - preload images?


      $main.animate({opacity: 0}, fadeSpeed, fadeEasingType, function(){
        window.scroll(0, 0);
        $main.empty();
        var lookbook = new Lookbook;
        var lookbookView = new LookbookView({
          collection: lookbook,
          el: $main[0]
        });
        lookbookView.render();
        _.delay(function(){ // pause the fade in a little.
          $("footer").animate({opacity: 1}, fadeSpeed, fadeEasingType);
          $main.animate({opacity: 1}, fadeSpeed, fadeEasingType, confirmMainOpacity());
        }, 500);

      });


    },

    // Populate and show all the categories.
    categories: function() {

      if(SHOP_CLOSED){
        $main.animate({opacity: 0}, fadeSpeed, fadeEasingType, function(){
          $main.animate({opacity: 1}, fadeSpeed, fadeEasingType, confirmMainOpacity());
          $main.html($('#shop-closed-content').html());
          watchShopClosedForm();
          observeFooterLinks();

        });

      } else {
        // Adding check to make sure backbone data exists before rendering
        if (Supreme.categories) {
          renderMain();
        } else {
        // If backbone data doesnt exist yet, wait a bit to check again.
          setTimeout(function() {
            renderMain();
          }, 750);
        }
      }

      function renderMain() {
        $('body').removeClass('checkout-loading');
        if(goLastPlace(Supreme.app)){return false; };
        showCartAndCheckout();
        _currentViewHash.categories = JSON.stringify(Supreme.categories).hashCode();
        // Preload some images.
        Supreme.categories.each(function(category){
          for(var i = 0; i < category.get('products').length; i++){
            // Just get the first 2 of each.
            if(i >= 2){
              break;
            }
            prefetchImage(category.get('products').at(i).get('image_url'));
          }
        });

        var categoryCollectionView = new CategoryCollectionView({
          collection: Supreme.categories,
          el: $main[0]
        });
        $main.animate({opacity: 0}, fadeSpeed, fadeEasingType, function(){
          markItemTimeViewed('categories');
          categoryCollectionView.render();
          $main.animate({opacity: 1}, fadeSpeed, fadeEasingType, function(){
            confirmMainOpacity();
            if(!window.IOS_APP && !_.isUndefined(window.navigator.standalone) && !window.navigator.standalone && _.isNull(readCookie('hasVisited'))){
              createCookie('hasVisited', '1', 100000);
            }

          });
        });
      }
    },
    // List products in category.
    categoryProductList: function(name) {
      $('body').removeClass('checkout-loading');
      if(goLastPlace(Supreme.app)){return false; };
      showCartAndCheckout();
      // Figure out which category we're going for.
      var category = Supreme.categories.find(function(c){
        return c.get('name') == name;
      });

      if(!_currentCategory){
        _currentCategory = singularCategoryName(name);
        _currentCategoryPlural = name;
      }      

      // Preload images.
      category.get('products').each(function(product){
        prefetchImage(product.get('image_url'));
      });
      _currentViewHash.categoryProductList = JSON.stringify(category.get('products')).hashCode();
      var productsView = new CategoryProductsView({
        collection: category.get('products'),
        el: $main[0],
        model: category
      });
      productsView.render();
      markItemTimeViewed('categoryProductList');
    },
    // Product detail view. Needs to be loaded remotely.
    // StyleId is optional.
    productDetail: function(productId, styleId){
      $('body').removeClass('checkout-loading');
      if (Backbone.history.getFragment().indexOf('zoom') > -1) {
        var redirectFragment = Backbone.history.getFragment().replace('/zoom', '');
        Supreme.app.navigate(redirectFragment, {trigger: true, replace: true});
      }

      if(goLastPlace(Supreme.app)){return false; };
      showCartAndCheckout();

      $('footer').hide();

      // Fish out some current product details from the pre-loaded data.
      var productInfo = Supreme.getProductOverviewDetailsForId(productId, allCategoriesAndProducts);

      // Not in the product info? It doesn't exist or is not live.
      if(_.isUndefined(productInfo)){
        Supreme.app.navigate("#", {trigger: true});
        return;
      }

      var product = new Product({
        id:         productId,
        name:       productInfo.name,
        price:      productInfo.price,
        price_euro: productInfo.price_euro,
        sale_price: productInfo.sale_price,
        sale_price_euro: productInfo.sale_price_euro,
        categoryName: productInfo.categoryName
      });

      _currentViewHash.product = JSON.stringify(productInfo).hashCode();

      // Was the _currentCategory not set? It means we got here directly. Record the category.
      
      if(!_currentCategory){
        _currentCategory = singularCategoryName(productInfo.categoryName);
        _currentCategoryPlural = productInfo.categoryName;
      }
    
      var tt = new TrackTiming('Mobile application', 'Show product detail');
      // Particularly long load here sometimes, let's show the loader.
      // $('body').addClass('loading');
      $main.animate({opacity: 0}, fadeSpeed, fadeEasingType, function(){
        // Only jump us back to top of we're far down.
        // if($(window).scrollTop() > 100){
        window.scrollTo(0, 0);
        // }

        $main.animate({opacity: 1}, fadeSpeed, fadeEasingType, confirmMainOpacity());
        $('footer').show();

        // Drop in the white square to show something is happening. Kind of a placeholder teaser.
        // This $(window)height bit is to keep footer stuff from jumping around.
        var placeholder = '<div id="product"><h2 id="name">' + productInfo.name + '</h2><p id="style-name">&nbsp;</p><div id="style-image"><div id="style-image-container" class="swipe loading" style="visibility: visible; "></div><div class="clearfix"></div></div></div><div id="product-widgets" class="clearfix  "><div id="widgets-container"><span class="price">&nbsp;</span><span id="cart-update"></span></div></div><div style="margin-bottom:' + $(window).height() + 'px;" id="product-details"><div id="product-details-content"><div id="styles"><ul id="style-selector"><li><div class="style-images"></div></li></ul><div class="clearfix"></div></div><p style="height:150px;" id="description">&nbsp;</p></div></div>';
        $main.html(placeholder);

        product.fetch({success: function(e){
          markItemTimeViewed(productId)

          // Did a style get passed in? Manually set it.
          if(!_.isUndefined(styleId)){
            product.set('selectedStyle', product.get('styles').get(styleId));
          } else {
            // Otherwise Set the first style as being selected.
            product.set('selectedStyle', product.get('styles').first());
          }

          product.get('styles').each(function(style){
            style.get('sizes').each(function(size){
              if(size.get('stock_level') > 0 && !_.isNull(sessionStorage.getItem('out_of_stock_' + size.get('id'))))
              // Clear this out of the sold out session storage if it's not sold out anymore.
              sessionStorage.removeItem('out_of_stock_' + size.get('id'));
            });
          });


          productDetailView = new ProductDetailView({
            model: product
          });

          // The polling timer. Only runs for the current product when on the product view.
          // Technically always will run, but will only get data under those conditions.
          window.clearInterval(productTimer);
          productTimer = setInterval(function(){
            productDetailViewPoller(productId);
          }, _productPollInterval);

          $main.html(productDetailView.render().el);
          $('#style-image-container').css('opacity', 0);
          window.productSwiper = Swipe(document.getElementById('style-image-container'), {
            speed: 200,
            startSlide: productDetailView.model.get('styles').indexOf(productDetailView.model.get('selectedStyle')),
            transitionEnd: function(index, elem){
              _isSwiping = false;
              var newStyle = productDetailView.model.get('styles').at(index);
              // This might be where we'd force the visible photo back to 0, but we'd rather show the last thing they looked at.
              productDetailView.model.set('selectedStyle', newStyle);
              productDetailView.updateUrl();
            },
            continuous: false,
            disableSwipe: productDetailView.model.get('styles').length == 1
          });

          $('#style-image-container').css({opacity: 1});
    
          // Preload all style images.
          product.get('styles').each(function(style) {
            if(iPad){
              prefetchImage(style.zoomedPhoto());
            } else {
              prefetchImage(style.productPhoto());
            }
          });

          tt.endTime().send();
        }});
      });
    },
    // Accepts an optional error message.
    cart: function(){
      $('body').removeClass('checkout-loading');
      if(goLastPlace(Supreme.app)){return false; };
      var cartView = new CartView({model: Supreme.app.cart});
      $main.animate({opacity: 0}, fadeSpeed, fadeEasingType, function(){
        Supreme.app.cart.fetch({success: function(e){
          cartView.render();
          Supreme.app.cart.lastError = ""; // Clear out any lingering errors.
          $main.animate({opacity: 1}, fadeSpeed, fadeEasingType, confirmMainOpacity());

          if(Backbone.history.fragment == "cart"){
            $('footer').css('opacity', 0)
            $("#goto-cart-link").hide();
            $("#checkout-now").show()
          }

        }});
      });
    },
    checkout: function(){
      $('body').removeClass('checkout-loading');
      if(goLastPlace(Supreme.app)){return false; };

      // If the cart is empty they can't get here, unless we're in native mode.
      if(!$('body').hasClass('for-native-checkout')){
        if(Supreme.app.cart.length() == 0){
          Supreme.app.navigate("#", {trigger: true});
          return;
        }
      }


      $main.animate({opacity: 0}, fadeSpeed, fadeEasingType, function(){
        var checkoutForm = new CheckoutForm();
        var checkoutView = new CheckoutView({
          model: checkoutForm
        });
        $.scrollTo(0);
        $main.html(checkoutView.render().el);
        $('select').selectric();

        checkoutView.captcha();

        if(IS_EU){ // force country change AFTER render, so that we always update ourselves correctly (e.g, to load in vat exception prices)
          checkoutView.countryChanged();
        }
        if(IS_US){ // force state change AFTER render, so that we always update ourselves correctly (e.g, to load in vat exception prices)
          checkoutView.stateChanged();
        }

        $main.animate({opacity: 1}, fadeSpeed, fadeEasingType, confirmMainOpacity());
        $('footer').css('opacity', 1)
        if(Backbone.history.fragment == "checkout"){
          $("#goto-cart-link").show().text('EDIT CART').addClass('edit');
          $("#checkout-now").hide()
        }
      });
    },
    chargeError: function(botError){
      $('body').removeClass('checkout-loading');
      var data = {};
      if(botError){
        data.botError = true;
      } else {
        data.botError = false;
      }
      showCartAndCheckout();
      if(goLastPlace(Supreme.app)){return false; };

      var chargeErrorView = new ChargeErrorViewTemplate({
        el: $main[0],
        model: data
      });
      chargeErrorView.render();
    },
    chargeErrorBot: function(){
      $('body').removeClass('checkout-loading');
      this.chargeError(true);
    },
    paypalConfirmOrder: function(){
      $('body').removeClass('checkout-loading');
      showCartAndCheckout();
      if(goLastPlace(Supreme.app)){return false; };

      // Fish out the ID and token from the URL and use that to load up the order details for display.
      var GETs = {};
      document.location.search.replace(/\??(?:([^=]+)=([^&]*)&?)/g, function () {
          function decode(s) {
              return decodeURIComponent(s.split("+").join(" "));
          }
          GETs[decode(arguments[1])] = decode(arguments[2]);
      });

      // Clear the cart.
      localStorage.clear();
      $('#cart-link').remove();
      eraseCookie('cart');
      Supreme.app.cart = new Cart();
      
      // Means we have a token from paypal and we can look up our order to fetch that data.
      $.getJSON('/mobile/paypal_confirmation.json?t=' + GETs.t + '&i=' + GETs.i, function(data){
        order = data.info;
        var orderConfirmationView = new OrderConfirmationView({
          el: $main[0],
          model: order
        });
        orderConfirmationView.render();
        // Need this on the HTML so we can know to show the mailing list checkbox.
        $('html').addClass('orderConfirm');
      });

      clearCookies();

    },
    confirmOrder: function(){
      $('body').removeClass('checkout-loading');
      showCartAndCheckout();
      if(goLastPlace(Supreme.app)){return false; };
      var order = {"id":1111111,"billing_name":"First Last","email":"name@example.com","purchases":[{"image":"//d17ol771963kd3.cloudfront.net/139173/ca/AqX9dg89pIg.jpg","product_name":"Digi Camo MA-1","style_name":"Pink Digi Camo","size_name":"Small","price":32800,"product_id":302678,"style_id":19276,"quantity":1},{"image":"//d17ol771963kd3.cloudfront.net/139652/ca/SZJzpgwa1Zs.jpg","product_name":"Contrast Stitch Pullover","style_name":"Navy","size_name":"Small","price":16800,"product_id":302683,"style_id":19300,"quantity":1}],"item_total":49600,"shipping_total":1000,"tax_total":4491,"total":55091,"currency":"$","store_credit":0,"discount_total":0,"created_at":"Feb 20 at 16:45","service":"UPS Ground","is_canada":false};

      var orderConfirmationView = new OrderConfirmationView({
        el: $main[0],
        model: order
      });
      orderConfirmationView.render();
    }



  });

  if(!ptr){
    setTimeout(function(){
      console.log("Main: ", $('#main').length);
      ptr = PullToRefresh.init({
        shouldPullToRefresh: function(){
          // Only want it on these pages:
          if($('#products').length == 0 && $('#categories-list').length == 0){
            return false;
          };
          // Don't want this engaging if you're already down the page.
          if($(window).scrollTop() > 50){
            return false;
          }
          return true;
        },
        onRefresh: function (done) {
          window._gaq.push(['_trackEvent', 'pull-to-refresh', 'pulled', Backbone.history.getFragment()]);
          loadDataForPoll(function(){
            done(); // end pull to refresh
          });
        }
      });
    }, 200);
  }


});



String.prototype.hashCode = function(){
    var hash = 0, i, char;
    if (this.length == 0) return hash;
    for (i = 0, l = this.length; i < l; i++) {
        char  = this.charCodeAt(i);
        hash  = ((hash<<5)-hash)+char;
        hash |= 0;
    }
    return hash;
};



// Used in a polling event inside the product view to see when it updates, and also when the app is resumed (via the SS15 iOS version)
function productDetailViewPoller(productId){
    var curRoute = currentRoute();
    var p = curRoute.params;
    if(!_.isUndefined(curRoute)
    && !_.isUndefined(curRoute.route)
    && !_.isUndefined(curRoute.params)
    && curRoute.route == 'productDetail'
    && productId == parseInt(p[0]) // only if the timer this was launched for is for the current product.
    ){

    var updatedProductInfo = Supreme.getProductOverviewDetailsForId(productId, allCategoriesAndProducts);

    // Load up that product anew.
    var updatedProduct = new Product({
        id:         productId,
        name:       updatedProductInfo.name,
        price:      updatedProductInfo.price,
        price_euro:      updatedProductInfo.price_euro,
        sale_price: updatedProductInfo.sale_price,
        sale_price_euro: updatedProductInfo.sale_price_euro,
        categoryName: updatedProductInfo.categoryName
      }); // Pull in the data.
      updatedProduct.fetch({success: function(m, r, e){

        // Mark this single product as having been updatede...
        markItemTimeViewed(productId);

        // Compare sold out styles now to sold out sizes before.
        var newSoldOutStates = JSON.stringify(updatedProduct.get('styles').map(function(style){
          return style.get('sizes').map(function(size){
            return size.get('stock_level') == 0;
          });
        }));

        var existingSoldOutStates = JSON.stringify(productDetailView.model.get('styles').map(function(style){
          return style.get('sizes').map(function(size){
            return size.get('stock_level') == 0;
          });
        }));
        // Sold out statuses changed?

        var params =  curRoute.params;
        if(productId == parseInt(params[0])
         && existingSoldOutStates != newSoldOutStates
        && !_.isUndefined(curRoute)
        && !_.isUndefined(curRoute.route)
        && !_.isUndefined(curRoute.params)
        && curRoute.route == 'productDetail'
        && params.length >= 1){
          // Reload!
          console.log('product poll reload');
          Supreme.app.productDetail(productId)
        }
      }});
    }  
}
;
var Supreme;
var iPad = navigator.userAgent.match(/iPad/i) != null;
var iPhone = navigator.userAgent.match(/iphone|ipod/i) != null;
var android = navigator.userAgent.match(/Android/i) != null;
var _isSwiping = false; // for the products.
var _isLookbookSwiping = false;
var _staleDataAge = 4000; // how old is 'old' data considered? In milliseconds. this checks our current view vs. the loaded data, and will refresh if necessary.
var _pollInterval = 15000; // how often do we hit the server for updated data?
var _productPollInterval = 15000; // how often do we hit the server for updated data whne we're in a product view? It's just that product.
var _currentCategory = false; // Track the category we're in, so we can work around the "'New' next product" bug.
var _currentCategoryPlural = false;
var _firstLaunched = true;
var popZoomTriggered = false;
// Lets us manage a hash of downloaded zoomed images and their download times.
// Key it to URL <-> download time in milliseconds.
var _zoomedImageDownloadSpeeds = {};
var _zoomedImageLoadOrder = []; // track the order the images were loaded, so we can drop the earlier images we load new ones.

// Some views (categories and category products) will get re-rendered on the fly when their content on the server changes.
// This way new products show up automatically. But we don't want to always refresh the view, only if there's a change.
// This variable tracks a hash of the contents of the current view. If it's different on subsequent polling load we'll refresh.
//
// TODO - if you open app and the current view is super old should we force you back to the homepage, fresh?
var _currentViewHash = {
  categories: "",
  categoryProductList: "",
  product: ""
};

window.setPushNotificationId = function(pnid) {
  window.pushNotificationId = pnid; 
  setTimeout(function() {
    if (window._gaq)
      window._gaq.push(['_trackEvent', 'push-notifications', 'received', pnid]);
  }, 100);
}

window.setClickedPushNotificationId = function(cpnid) {
  window.ClickedPushNotificationId = cpnid; 
  setTimeout(function() {
    if (window._gaq)
      window._gaq.push(['_trackEvent', 'push-notifications', 'clicked', cpnid]);
  }, 100);  
}




window.appEnteredForeground = function(){
  mixpanelTrack("App Open");
  
  if (window.ClickedPushNotificationId && window.ClickedPushNotificationId.match(/^u:/)) {

    setTimeout(function() {
      var url = window.ClickedPushNotificationId.replace(/^u:/, '');
      window.ClickedPushNotificationId = null;
      Supreme.app.navigate(url, {trigger: true});
    }, 100);
  }





  // Can be called by the app when it enters foreground, when it's asleep. Triggers a reload of data.
  loadDataForPoll();
  // Are we looking at a specific product? Refresh it too:
  var current_route = currentRoute();
  if(current_route.route == 'productDetail'){
    if(!_.isUndefined(current_route.params) && current_route.params.length > 0){
      var productId = current_route.params[0];
      productDetailViewPoller(productId);
    }
  }
}

window.goToDeepLink = function(url) {
  setTimeout(function() {
    alert(url);
  }, 100);
}

function TrackTiming(category, variable, opt_label) {
  this.category = category;
  this.variable = variable;
  this.label = opt_label ? opt_label : undefined;
  this.startTime;
  this.endTime;
  return this;
}

TrackTiming.prototype.startTime = function() {
  this.startTime = new Date().getTime();
  return this;
}

TrackTiming.prototype.endTime = function() {
  this.endTime = new Date().getTime();
  return this;
}

TrackTiming.prototype.send = function() {
  var timeSpent = this.endTime - this.startTime;
  window._gaq.push(['_trackTiming', this.category, this.variable, timeSpent, this.label]);
  return this;
}

var load_page_tt = new TrackTiming('Mobile application', 'Initial loading');
load_page_tt.startTime();


(function() {
  var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
  ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
  var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();


_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g,
    evaluate : /\{\[([\s\S]+?)\]\}/g
};

var soldOutMessage = IS_JAPAN ? "カート内にある商品で完売してしまった商品があります。ご注文手続きに進む前にカートから削除してください。" : "Some of the items in your cart are now sold out. Remove them before check out.";
var productDetailView;
var scroller;
var categoryListTemplate = '<div id="categories-list" class="section"></div>';
var productListTemplate = '<div id="products" class="section"><h2></h2><ul></ul></div>';
var categoryProductListItemViewSize = (isHiRes() ? 50 : 45);
var categoryProductListItemView = '<div class="clearfix"><img height="' + categoryProductListItemViewSize + '" width="' + categoryProductListItemViewSize + '" src="{{ image_url }}"><span class="info"><span class="name">{{ name }}</span>{[if(new_item && !this.model.isOnSale()){ ]} <span class="new">new</span>{[ } ]}{[if(this.model.isOnSale()){ ]} <span class="sale">sale</span>{[ } ]}</span></div>';

// Goes inside the #style bit in the product detail template.
var styleDetailTemplate = '<div id="style-image-container" class="swipe"><div class="swipe-wrap"></div></div><div class="clearfix"></div>';

var scrollSpeed = 300;
var fadeSpeed = 400; // The fade speed starts out much longer than usual so our content initially loads in visibly smoother. After the site is initialized we speed it up significantly.
var fadeEasingType = 'ease-out';

$(document).ready(function(){
  setHiResClass();

  $(window).resize(function(){
    setHiResClass();
  });

  Supreme = {
    // Given a product ID and the list of category/product data, returns
    // that product's info.
    getProductOverviewDetailsForId: function(productId, productData){
      var foundProduct;
      _.each(productData.products_and_categories, function(products, categoryName){
        var p = _.find(products, function(product){
          return product.id == productId;
        });
        if(!_.isUndefined(p)){
          foundProduct = p;
          foundProduct.categoryName = categoryName;
          return;
        }

      });
      return foundProduct;
    }
  }


  if(iPad){
    $('body').addClass('ipad');
  }
  
  if (!navigator.userAgent.match(/Supreme-native\/(.*?) /i)) {
    $('body').addClass('not-native-app');
  }

  if(iPad || iPhone){
   $('body').addClass('idevice'); 
  }

  FastClick.attach(document.body);

  if (window.screen.height==568) { // iPhone 4"
      document.querySelector("meta[name=viewport]").content="width=320.1, initial-scale=1.0, maximum-scale=1.0, user-scalable=no";
  }

  observeFooterLinks();

  // localStorage validity test.

  var shoppingSessionId = readCookie('shoppingSessionId');

  // Do we have the shoppingSessionId cookie?
  // If not clear localstorage and we'll set the value anew both as a cookie and in localstorage.
  if(_.isNull(shoppingSessionId)){
    localStorage.clear();
    setSessionIDs();
  } else {
    // Do we have it but it's not in localStorage? This would also occur if localStorage doesn't have it.
    // Clear localStorage.
    if(parseInt(localStorage.getItem('shoppingSessionId')) != parseInt(shoppingSessionId)){
      // TODO - what changed with this?
      localStorage.clear();
      eraseCookie('shoppingSessionId'); // Clear out the cookie, we'll start again.
      setSessionIDs();
    } else {
      // If we have it and it matches localStorage we're all good.
    }
  }

  var campaign_origin;
  if (campaign_origin = location.search.match(/utm_medium=([a-z]+)/))
    createCookie('origin', campaign_origin[1],1);
  if (document.referrer.match(/facebook.com\//))
    createCookie('origin', 'facebook',1);


  // Preset all our categories and products in those categories.
  Supreme.categories = new Categories();

  // If allCategoriesAndProducts doesn't yet exist, pause, reload and try again.
  if (allCategoriesAndProducts) {
    Supreme.categories.populate(allCategoriesAndProducts);
  } else {
    loadDataForPoll();
    setTimeout(Supreme.categories.populate(allCategoriesAndProducts), 250);
  }

  if(allCategoriesAndProducts.sale){
    if($('#discount_banner').length == 0){
      $('#main').before('<p id="discount_banner">' + allCategoriesAndProducts.sale_blurb + '</p>');
    }
  }

  $('.supreme-navigation').on('click', function() {
    var $html = $('html');

    if ($html.hasClass('activate-back') && !$html.hasClass('is-zoomed') && !$html.hasClass('static-view')) {
      var bits = Backbone.history.fragment.split('/');

      if (Backbone.history.fragment == 'lookbook') {
        // If you're in the lookbook, go back to main categories page.
        Supreme.app.navigate('categories', {trigger: true});
      } else if (bits[0] === 'categories') {
        // If you're in the categories subview, go back to main categories page.
        Supreme.app.navigate('categories', {trigger: true});
      } else if (bits[0] === 'products') {
        // If you're in a product, go back to the parent category page.
        Supreme.app.navigate('categories/' + _currentCategoryPlural, {trigger: true});
      } else {
        // For anything else, just step back in hash history by one step.
        window.history.back();
      }
      return false;
    }
  });

  // Check if we're old, and if the data is old too, reload.

  setInterval(function(){
    if(SHOP_CLOSED){return;}
    if(!_.isUndefined(currentRoute()) && !_.isUndefined(currentRoute().route)){
      var current_route = currentRoute();
      if(current_route.route == 'categories' && itemViewIsStale('categories')){
        markItemTimeViewed('categories');
        if(JSON.stringify(Supreme.categories).hashCode() != _currentViewHash.categories){
          Supreme.app.categories();
        }
      } else if(current_route.route == 'categoryProductList' && itemViewIsStale('categoryProductList')){
        markItemTimeViewed('categoryProductList');
        // Need the current categories products to hash this out.
        var category = Supreme.categories.find(function(c){
          return c.get('name') == currentRoute().params[0];
        });        
        if(JSON.stringify(category.get('products')).hashCode() != _currentViewHash.categoryProductList){
          Supreme.app.categoryProductList(current_route.params[0]);
        }
      } else if(current_route.route == 'productDetail'){
        if(!_.isUndefined(current_route.params) && current_route.params.length > 0){
          var productId = current_route.params[0];
          if(itemViewIsStale(productId)){ // older than 30 seconds?
            markItemTimeViewed(productId); // Mark as updated so we don't accidently dupe up.
          }
        }
      }
    }
  }, 500);

  // Periodically reload the data.  
  setInterval(function(){
    loadDataForPoll();
  }, _pollInterval);
  


  // Gear up the global vart.
  Supreme.app = new AppRouter;
  Supreme.app.cart = new Cart();

  if(_.isNull(sessionStorage.getItem('hasVisited'))){
    // Make sure we're all clear if on first activity of session the cart is empty.
    if(Supreme.app.cart.length() == 0){
      clearCookies();
    };
    sessionStorage.setItem('hasVisited', 1);
  }

  Supreme.app.cartLinkView = new CartLinkView({model: Supreme.app.cart});
  $('header').prepend(Supreme.app.cartLinkView.render().el);


  // This here is triggered after each route change.
  Backbone.history.bind('route', function(router, route, args) {
    setLastVisitedFragment();
    _gaq.push(['_trackPageview', '/mobile/' + Backbone.history.fragment]);

    var bits = Backbone.history.fragment.split('/');

    if ((Backbone.history.fragment === 'categories' && bits[0] === 'categories') || (!Backbone.history.fragment))   {
      $('html').attr('class', Backbone.history.fragment + ' ' + bits[0] + ' index-route'); // Index route ( dont show back arrow )
    } else {
      $('html').attr('class', Backbone.history.fragment + ' ' + bits[0] + ' activate-back'); // Not index route ( show back arrow )
    }

    // Weird thing - need the categories class if its not set on load,
    // which it won't be on the homepage.
    if(Backbone.history.fragment == ""){
      $('html').addClass('categories');
    }

    // In shop closed mode we want to make sure the signup field is reset when you tap back to the homepage.
    if(SHOP_CLOSED){
      $('#shop_closed p.copy').show();
      $('#email_field').show();
      $('#eu_field').show();
      $('.checkbox-container').show();
    }

  });

  // Start Backbone history a neccesary step for bookmarkable URL's
  Backbone.history.start();

  setCurrentLangToggle(currentLang())


  /* ************* */

  // When we first load remove the loader.

  $('#intro-loading').animate({opacity: 0}, fadeSpeed, fadeEasingType, function(){
    $(this).remove();
    fadeSpeed = 100; // The fade speed starts out much longer than usual so our content initially loads in visibly smoother. After the site is initialized we speed it up significantly. This is that speed up.
  });
  _.delay(function(){
    $('footer').addClass('first-loaded').animate({opacity: 1}, fadeSpeed, fadeEasingType);
  }, 700);
  load_page_tt.endTime().send();


   // Language setting stuff.
  // No clue why click was behaving weirdly, but it was. So, touchstart. Also disabled this for fastclick via a needsclick class on the element.
   $('#current-lang').on('touchstart', function(e){
    showLanguageSetter();
    e.preventDefault();
   });





});


// Set a new language setting to override the one set by NGINX and Varnish. This new value is then read upstream so the cached pages that are served can be adjusted.
function setCurrentLang(lang){
  createCookie('lang', lang, 100000);
  createCookie('langChanged', 1, 100000); // Track if they manually changed their language.
}

function currentLang(){
  var default_lang = 'en';
  if(readCookie('lang') == null){
    return default_lang;
  } else {
    return readCookie('lang');
  }
}

// Show the language setter, abs. positioned at the given coords.
function showLanguageSetter(top, left){

  var languageBg = $('<div id="language-bg" style="z-index:2;opacity:0;position:fixed;top:0;bottom:0;left:0;right:0;background:rgba(0, 0, 0, .25);"></div>');
  $('body').append(languageBg);
  var setter = $('<ul id="language-setter"><li class="en">UK</li><li class="de">DE</li><li class="fr">FR</li></ul>');
  setter.attr('class', currentLang());
  $('body').append(setter);
  var setterEl = $('#language-setter');
  setterEl.css({
    position: 'fixed',
    top: '50%',
    left: '50%',
    marginLeft: -setterEl.width()/2,
    marginTop: -setterEl.height()/2
  });
  

  languageBg.animate({opacity: 100}, {duration: 200, easing:fadeEasingType});
  setter.animate({opacity: 100}, {duration: 200, easing:fadeEasingType});

  $('html').addClass('lang-changing');

  $(languageBg).click(function(e){
    hideLanguageSetter();
    e.preventDefault();
  });


  setterEl.find('li').click(function(e){
    e.stopImmediatePropagation();
    var lang = $(this).attr('class').toLowerCase();
    setCurrentLang(lang);
    setCurrentLangToggle(lang);
    _.delay(function(){
      window.location.reload() // Need to reload the page so varnish will serve the correct data.
    }, 20); // gives time for the flag to change.
  });
}

// Update the toggle for the given language.
function setCurrentLangToggle(lang){
  var displayLang = lang.toUpperCase();
  if(displayLang == 'EN'){
    displayLang = 'UK';
  }
  $('#current-lang').attr('class', lang.toLowerCase()).text(displayLang);
}

// Hide the language setter. Expects a callback to be triggered after it fades.
function hideLanguageSetter(){
  $('html').removeClass('lang-changing');
  // $('#language-bg').fadeOut('fast', function(){ $(this).remove() });
  $('#language-bg').animate({opacity: 0}, {duration: 200, easing:fadeEasingType, complete:function(){
    $(this).remove();
  }});
  // $('#language-setter').fadeOut('fast', function(){ $(this).remove() });
  $('#language-setter').animate({opacity: 0}, {duration: 200, easing:fadeEasingType, complete:function(){
    $(this).remove()
  }});
}



function getNextProductFromId(productId){
  var foundProduct;
  // What category are we in now?
  var categoryToChooseFrom = _currentCategoryPlural;
  if(_.isUndefined(_currentCategoryPlural)){
    _currentCategoryPlural = 'new';
  }
  
  var products = allCategoriesAndProducts.products_and_categories[_currentCategoryPlural];

  for(var i = 0; i < products.length; i++){
    if(products[i].id == productId){
      // Get out the next one.
      // If the next one is undefined then return the first.
      if(_.isUndefined(products[i + 1])){
        foundProduct = products[0];
      } else {
        foundProduct = products[i + 1];
      }
    }
  }
  
  return foundProduct;

}


// Given a value of GBPs returns Euros.
// Assumes a conversion constant has been defined.
//
function GBPtoEuro(GBP){
  return GBP_TO_EURO * GBP;
}

// Given value in cents returns a formatted currency.
// If an additional currencyOverride is provided it will be used instead of the default.
//
function formatCurrency(cents, currencyOverride, forceRound) {
    var str;
    cents = cents/100;
    cents = _.isNaN(cents) || cents === '' || cents === null ? 0.00 : cents;
    if(cents % 1 == 0.00){
      str = addCommas(parseFloat(cents).toFixed(0));
    } else {
      str = addCommas(parseFloat(cents).toFixed(2));
    }

    if(!_.isUndefined(forceRound) && forceRound && str.indexOf(",") == -1){
      str = Math.round(str); // not if there are commas, we'll get a NaN
    }

    if(!_.isUndefined(currencyOverride)){
      if (currencyOverride.length > 1)
        return str + ' ' + currencyOverride;
      else
        return currencyOverride + str;
    }


    if (IS_JAPAN)
      return '¥' + str;
    else if(IS_EU)
      return (LANG.currency == "eur" ? '€' : '£') + str;
    else
      return '$' + str;

}

function addCommas(nStr)
{
  nStr += '';
  var x = nStr.split('.');
  var x1 = x[0];
  var x2 = x.length > 1 ? '.' + x[1] : '';
  var rgx = /(\d+)(\d{3})/;
  while (rgx.test(x1)) {
    x1 = x1.replace(rgx, '$1' + ',' + '$2');
  }
  return x1 + x2;
}

function singularCategoryName(plural){
  return singularizedCategories[plural];
}

function showLoader(){
  var loader = $('<div id="main-loader"></div>');
  var containerOffset = $('#container').offset();
  loader.css({
    top: containerOffset.top,
    left: containerOffset.left,
    width: containerOffset.width,
    height: containerOffset.height,
  });
  $('#container').before(loader);
  loader.animate({opacity: 1}, fadeSpeed, fadeEasingType);
}

function hideLoader(){
  $('#main-loader').animate({opacity: 0}, fadeSpeed, fadeEasingType, function(){
    $('#main-loader').remove();
  });
}

function createCookie(name,value,days) {
  if (days) {
    var date = new Date();
    date.setTime(date.getTime()+(days*24*60*60*1000));
    var expires = "; expires="+date.toGMTString();
  }
  else var expires = "";
  document.cookie = name+"="+value+expires+"; path=/";
}


function readCookie(name) {
  var nameEQ = name + "=";
  var ca = document.cookie.split(';');
  for(var i=0;i < ca.length;i++) {
    var c = ca[i];
    while (c.charAt(0)==' ') c = c.substring(1,c.length);
    if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
  }
  return null;
}

function eraseCookie(name) {
  createCookie(name,"",-1);
}

function isNamePrintable(name){
  return !_.isUndefined(name) && !_.isNull(name) && name != "N/A" && name.replace(/^\s+|\s+$/g, '') != "" && name != '&nbsp;';
}

function getNumberOfJumps(){
  var lastNumber = localStorage.getItem('numberOfJumps');
  if(_.isNull(lastNumber)){
    localStorage.setItem('numberOfJumps', 0);
    return 0;
  }
}



function getItemTimeViewed(itemName){
  return localStorage.getItem(itemName + '_updated_at')  ;
}

// Given a product ID mark the time it was viewed.
// We do this so we can refresh faster when it hasn't been viewed for a while.
function markItemTimeViewed(itemName){
  localStorage.setItem(itemName + '_updated_at', Date.now());
}

function itemViewIsStale(itemName){
  var lastViewed = getItemTimeViewed(itemName);
  if(!lastViewed){return false;} // never checked? it's not stale.
  return Date.now() - lastViewed >= _staleDataAge;
}

function incrementNumberOfJumps(){
  var lastNumber = localStorage.getItem('numberOfJumps');
  if(!_.isNull(lastNumber)){
    localStorage.setItem('numberOfJumps', lastNumber + 1);
  } else {
    localStorage.setItem('numberOfJumps', 0);
  }
}

// Used before each route to record where the user was previously and re-route them if needed.
function goLastPlace(app){

  if(_.isUndefined(window.navigator.standalone) || !window.navigator.standalone){
    return false;
  }

  // Only bother if we haven't run already, don't want to do this on every route.
  if(_.isNull(sessionStorage.getItem('hasTriggeredRoute'))){

    // Now we'll know, going forward, that this wasn't the first event of the session.
    sessionStorage.setItem('hasTriggeredRoute', 1);

    // Do we have a last frag marker? If not don't do anything, but record where we're at.
    if(_.isNull(getLastVisitedFragment())){
      // console.log('[goLastPlace] frag not set, do nothing.');
      return false;
    } else {
      // If we do have a last frag marker we'll go there.
      // Unless we're there of course.
      if(getLastVisitedFragment() == Backbone.history.fragment){
        // console.log('[goLastPlace] already here, doing nothing: ' + Backbone.history.fragment);
        return false;
      } else {
        // console.log('[goLastPlace] new place, recording and visiting: ' + Backbone.history.fragment )
        app.navigate(getLastVisitedFragment(), {trigger: true});
        return true;
      }
    }
  }
  return false;
}

function showCartAndCheckout(){
  // Do this fragment check to prevent them from being shown at weird times, like if the user tapped a non-checkout view, then real quick hit the cart again. In some cases this would trip up the behavior here.
  if(Backbone.history.fragment != 'checkout'){
    $("#goto-cart-link").show().text(Supreme.app.cart.length()).removeClass('edit');
    $("#checkout-now").show()
  }
  if(Backbone.history.fragment != 'cart' && $('footer').hasClass('first-loaded')){
    $('footer').css('opacity', 1)
  }
}

// Quick n' dirty image preloader. Used to kick start image loading perhaps before the view is fully ready to fade in or transition.
function prefetchImage(src){
  var img = new Image();
  $(img).attr('src', src);
}


function storageKeyIsProduct(key){
  if(key == 'lastMobileApiUpdate' || key == "_cb_cp" || key == 'home' || key == 'lastFragment' || key == 'shoppingSessionId' || key.indexOf('updated_at') !== -1  || key.indexOf('_qty') !== -1){
    return false;
  } else {
    return true;
  }
}

function setSessionIDs(){
  var currentTime = new Date().getTime();
  createCookie('shoppingSessionId', currentTime, 1);
  localStorage.setItem('shoppingSessionId', currentTime);
}

function setLastVisitedFragment(){
  createCookie('lastVisitedFragment', Backbone.history.fragment, 182); // 6 months about.
}

function getLastVisitedFragment(){
  return readCookie('lastVisitedFragment');
}

// Used by the native app to pipe in cart data necessary to create the localstorage, as it would be generated by the mobile app when accessed through the web.
// The regular mobile web version relies on localstorage to maintain a robust set of data needed for checkout, but this isn't built by the native app. So we fake it here.
// Expects a hash of size IDs as the values, with size, style, and product data hashes as values.

function set_local_storage(localstorage_data){
  for (var size in localstorage_data) {
      if (localstorage_data.hasOwnProperty(size)) {
          localStorage.setItem(size, JSON.stringify(localstorage_data[size]));
      }
    }
}

// On first load we'll fire off an event saying we just launched in standalone mode.
if(!_.isUndefined(window.navigator.standalone) && window.navigator.standalone){
  _gaq.push(['_trackEvent', "isStandalone", "launched"]);
}


function observeFooterLinks(){
  $('footer ul li span').bind('click', function(){
      if($(this).attr('id') == 'lookbook-footer-link'){
        if(Backbone.history.fragment != 'lookbook'){
          $.scrollTo(0, 0, function(){
            Supreme.app.navigate("lookbook", {trigger: true});
          });
        } else { // don't hide the footer if you're already on the footer.
          $.scrollTo(0, scrollSpeed, function(){
            Supreme.app.navigate("lookbook", {trigger: true});
          });
        }

      } else {
        var self = this;
        $.scrollTo(0, scrollSpeed, function(){
          var staticContentView = new StaticContentView();
          staticContentView.render($(self).attr('id'));
          $('html').addClass('static-view');
        })
      }
  });
  $('#full-site-link').click(function(){
    window._gaq.push(['_trackEvent', 'mobile-full-site-link']);
  });
}

function logError(errorMessage, errorData){
  if (window.trackJs)
      
  var fullError = $.extend({type: 'mobileChargeError'}, errorData);
  fullError = $.extend({errorMessage: errorMessage }, fullError);
  $.ajax({
    type: 'GET',
    url: 'http://app.supremenewyork.com/mobile_error',
    dataType: 'jsonp',
    data: fullError
  });
}



function currentRoute() {
    var Router = Supreme.app,
        fragment = Backbone.history.fragment,
        routes = _.pairs(Router.routes),
        route = null, params = null, matched;

    matched = _.find(routes, function(handler) {
        route = _.isRegExp(handler[0]) ? handler[0] : Router._routeToRegExp(handler[0]);
        return route.test(fragment);
    });

    if(matched) {
        // NEW: Extracts the params using the internal
        // function _extractParameters
        params = Router._extractParameters(route, fragment);
        route = matched[1];
    }

    return {
        route : route,
        fragment : fragment,
        params : params
    };
}


// Determine whether the current screen is hi density.
// Taken from modernizr-retina-test.
function isHiRes(){
  var dpr = window.devicePixelRatio ||
  // fallback for IE
      (window.screen.deviceXDPI / window.screen.logicalXDPI) ||
  // default value
      1;
  return !!(dpr > 1);  
}

// These classes help us size retina and larger image photos.
function setHiResClass(){
  if(isHiRes()){
    $('body').addClass('hi-res');
    if($(window).width() > 320){
      $('body').addClass('wide');
    }
  }  
}

function isHiResAndWide(){
  return isHiRes() && $(window).width() > 320;
}

function median(values) {
  values.sort( function(a,b) {return a - b;} );
  var half = Math.floor(values.length/2);
  if(values.length % 2){
    return values[half];
  } else {
    return (values[half-1] + values[half]) / 2.0;
  }
}


function loadDataForPoll(callback){
  if(SHOP_CLOSED){return;}
  $.getJSON('/mobile_stock.json', function(data, status, xhr){
    // mobile versioning
    var reloading = false;
    if(typeof window.splayver === "undefined") {
      if (xhr.getResponseHeader("X-Splay-Version") != null) {
        if (xhr.getResponseHeader("X-Splay-Version").match(/^[0-9a-f]{16}$/) != null && xhr.getResponseHeader("X-Splay-Version").match(/^[0-9a-f]{16}$/).length == 1) {
          if (xhr.getResponseHeader("X-Splay-Version").match(/^[0-9a-f]{16}$/)[0] == xhr.getResponseHeader("X-Splay-Version")) {
            window.splayver = xhr.getResponseHeader("X-Splay-Version");
          }
        }
      }
    } else {
      if (xhr.getResponseHeader("X-Splay-Version") != null && xhr.getResponseHeader("X-Splay-Version") != window.splayver) {
        if (xhr.getResponseHeader("X-Splay-Version").match(/^[0-9a-f]{16}$/) != null && xhr.getResponseHeader("X-Splay-Version").match(/^[0-9a-f]{16}$/).length == 1) {
          if (xhr.getResponseHeader("X-Splay-Version").match(/^[0-9a-f]{16}$/)[0] == xhr.getResponseHeader("X-Splay-Version")) {
            window.splayver = xhr.getResponseHeader("X-Splay-Version");
            reloading = true;
            location.reload();
          }
        }
      }
    }

    if (!reloading) {
      window.release_week = data.release_week;
      window.release_date = data.release_date;

      handleApiTimestamp(data.last_mobile_api_update);
      // Assume we'll have Accessories. If we don't it means the data is junk and we don't want it.
      if(!_.isUndefined(data.products_and_categories)){
        
        if(data.discount){
          if($('#discount_banner').length == 0){
            $('#main').before('<p id="discount_banner">' + data.discount_blurb + '</p>');
          }
        }
        SALE_VISIBLE = data.on_sale;

        // Re-populate our lists.
        allCategoriesAndProducts = data;
        Supreme.categories = new Categories();
        Supreme.categories.populate(allCategoriesAndProducts);


        // Is there a callback? Call it.
        if(!_.isUndefined(callback)){
          console.log("callback!");
          callback();
        }

      // Determine what to re-render based on the current fragment.
      // We only ever do it on the list of categories view or list of products-in-category view.
      // When we do refresh there's the flash of a reload. Don't want to always do that, only when there's actual new content.
      // So, when a view is rendered, we'll generate a hash based on its contents, and on re-load we'll see
      // if that hash has changed. If it does we'll re-render the view from scratch, otherwise nothing will happen.

      if(!_.isUndefined(currentRoute()) && !_.isUndefined(currentRoute().route)){
        var current_route = currentRoute().route;
        if(current_route == 'categories'){
          if(JSON.stringify(Supreme.categories).hashCode() != _currentViewHash.categories){
            Supreme.app.categories();
          }
        } else if(current_route == 'categoryProductList'){
          // Need the current categories products to hash this out.
          var category = Supreme.categories.find(function(c){
            return c.get('name') == currentRoute().params[0];
          });
          if(_.isUndefined(category)){
            Supreme.app.navigate("#", {trigger: true});
          } else if(JSON.stringify(category.get('products')).hashCode() != _currentViewHash.categoryProductList){
            Supreme.app.categoryProductList(currentRoute().params[0]);
          }
        }
      }
    }
  }
});
}

function mixpanelTrack(event) {
  try {
    if (!mixpanel)
      return false;

    mo = {}
    mo['Event Name'] = event;
    mo['URL'] = location.pathname;
    mo['Season'] = SEASON_NO;
    mo['Release Date'] = window.release_date;
    mo['Release Week'] = window.release_week;
    mo['Page Name'] = document.title;
    mo['Device Type'] = "Mobile";

    obj = [].slice.call(arguments)[1];


    if (event == "Purchase Attempt") {
      $.each(obj, function(index, val) {
        mixpanel.track('Purchase Attempt', $.extend(mo, val))
      });

    } else {
      if (obj) 
        mo = $.extend(mo, obj);
      
      mixpanel.track(event, mo);
    }
  } catch(err) {
    console.log(err);
  }
}


// We used to hit /mobile/clear to make sure every cookie and rails session was cleared.
// Now we just do it client side, with this.
function clearCookies(){
  localStorage.clear();
  eraseCookie('shoppingSessionId');
  eraseCookie('_supreme_sess');
  eraseCookie('cart');
  eraseCookie('pure_cart');
  eraseCookie('cart');  

  // If we *really* wanted to reset everything, we'd include these lines.
  // But we don't, the existing app logic does that.
  // $('#cart-link').remove();
  // Supreme.app.cart = new Cart();
  // Supreme.app.cartLinkView = new CartLinkView({model: Supreme.app.cart});
  // $('header').prepend(Supreme.app.cartLinkView.render().el);   
}

if (window.IOS_APP) {
  (function(){
    var open = window.XMLHttpRequest.prototype.open,
       send = window.XMLHttpRequest.prototype.send,
       SCHEME = 'ajax',
       _url, _method, _data, onReadyStateChange;

    SCHEME = 'ajax';

    ios = function(action, status, data){
      var infoObj = {url:_url, method: _method, data: data};
      if(status !== null){
        infoObj.status = status;
      }
      window.location = SCHEME +'://' + action + '?xhr='+JSON.stringify(infoObj)
    }

    window.XMLHttpRequest.prototype.open = function(method, url){
      _method = method;
      _url = url;
      return open.apply(this, arguments);
    }

    newOnReadyStateChange = function(e) {
      if (this.readyState === 4) {
        if(this.status == 200 || this.status == 304){
          ios('completed', this.status, '');
        } else if (this.status > 500) {
          ios('error', this.status, this.statusText);
          error = {url: _url, status: this.status, statusText: this.statusText};
          $.ajax({
            type: 'GET',
            url: 'http://app.supremenewyork.com/mobile_error',
            dataType: 'jsonp',
            data: error
          });

        }

      }

      return this._onreadystatechange.apply(this, arguments);
    }


    window.XMLHttpRequest.prototype.send = function(data){ 
      // Remove previous override
      if(this.onreadystatechange.__mine != null && this.onreadystatechange.__updated == null) {
        this.onreadystatechange = newOnReadyStateChange;
      } else if (this.onreadystatechange.__updated == null) {
        this._onreadystatechange = this.onreadystatechange;
        this.onreadystatechange = newOnReadyStateChange;
      }
      ios('send', null, data);
      return send.apply(this, arguments);
    }

    newOnReadyStateChange.__updated = true;
    newOnReadyStateChange.__mine = true;

  })();
}
;























