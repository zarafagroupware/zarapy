var AutoResizer = function (textArea, options) {
  var self = this;

  this.$textArea = $(textArea);
  this.minHeight = this.$textArea.height();

  this.options = $.extend({}, $.fn.autoResizer.defaults, options)

  this.$shadowArea = $('<div></div>').css({
      position: 'absolute',
      top: -10000,
      left: -10000,
      fontSize: this.$textArea.css('fontSize') || 'inherit',
      fontFamily: this.$textArea.css('fontFamily') || 'inherit',
      lineHeight: this.$textArea.css('lineHeight') || 'inherit',

      /* this helps a bit */
      paddingTop: this.$textArea.css('paddingTop') || 'inherit',
      paddingBottom: this.$textArea.css('paddingBottom') || 'inherit',
      paddingLeft: this.$textArea.css('paddingLeft') || 'inherit',
      paddingRight: this.$textArea.css('paddingRight') || 'inherit',

      /*
      But once you add borders to a box-sizing: border-box textarea,
      things go very wrong and this doesn't help.
      */
      borderTopWidth: this.$textArea.css('borderTopWidth') || 'inherit',
      borderBottomWidth: this.$textArea.css('borderBottomWidth') || 'inherit',
      borderLeftWidth: this.$textArea.css('borderLeftWidth') || 'inherit',
      borderRightWidth: this.$textArea.css('borderRightWidth') || 'inherit',

      resize: 'none'
    }).appendTo(document.body);

  var startWidth = this.$textArea.width() || $(window).width();
  this.$shadowArea.width(startWidth);

  if (this.options.resizeOnChange) {
    function onChange() {
      window.setTimeout(function() {
        self.checkResize();
      }, 0);
    }
    this.$textArea.change(onChange).keyup(onChange).keydown(onChange).focus(onChange);
  }

  this.checkResize();
};

 AutoResizer.prototype = {
  constructor: AutoResizer,
  checkResize: function() {
    // No sense in auto-growing non-visible textarea, which height of 0 implies
    if (this.$textArea.height() === 0) {
      return;
    }
    // If this is first time we've seen text area rendered, remember the height
    if (this.minHeight === 0) {
      this.minHeight = this.$textArea.height();
    }
    // If the text area has changed in size past a certain threshold of difference
    // like when it becomes visible or viewport changes
    if (this.$textArea.width() !== 0 && Math.abs(this.$shadowArea.width() - this.$textArea.width()) > 20) {
      this.$shadowArea.width(this.$textArea.width());
    }

    var val = this.$textArea.val().replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/&/g, '&amp;')
            .replace(/\n/g, '<br/>&nbsp;');

    if ($.trim(val) === '') {
        val = 'a';
    }
    this.$shadowArea.html(val);
    var nextHeight =  Math.max(this.$shadowArea[0].offsetHeight + 20, this.minHeight);
    if (!this.prevHeight || nextHeight != this.prevHeight) {
      this.$textArea.css('height', nextHeight);
      this.prevHeight = nextHeight;
    }
  }
};


$.fn.autoResizer = function ( option ) {
  return this.each(function () {
    var $this = $(this)
      , data = $this.data('autoresizer')
      , options = typeof option == 'object' && option
    if (!data) $this.data('autoresizer', (data = new AutoResizer(this, options)))
    if (typeof option == 'string') data[option]()
    else data.checkResize()
  })
}

$.fn.autoResizer.defaults = {
  resizeOnChange: true
};

$.fn.autoResizer.Constructor = AutoResizer;

$('textarea').autoResizer();

