// @import /js/lib/mustache.js
Array.prototype.indexOf = Array.prototype.indexOf || function(item) {
  var index = -1;
  for (var i = 0, len = this.length; i < len; i++) {
    if (this[i] === item) return i;
  }
  return index;
};
String.prototype.lastChar = function() {
  return this.charAt(this.length - 1);
};
/**
* Textarea '@' tag suggestion.
* @author: ktmud <jesseyang@douban.com>
*/
(function($) {
  //{{{
  var pre,
  node_suglist,
  txtMax = 140,
  activeIdx = 0,
  activeLeads = 0,
  userFlag = '', // save id & name
  textareaValTemp = '',
  TMPL_SUGGEST_OVERLAY= '<div id="db-tagsug-list" class="suggest-overlay"></div>',
  oBody = $(document.body),
  reg_space = / /g,
  reg_lt = /</g,
  reg_gt = />/g,
  reg_codetag = /<\/?code>/g,
  reg_btag = /<(\/|\\\/)?b>/g,
  reg_regchar = /(\\|\+|\:|\*|\/|\||\$|\?|\^|\[|\]|\(|\)\.)/g,
  blank_char = $.browser.version < 7 ? '&nbsp;' : 'x',
  ie_old = $.browser.msie && $.browser.version < 9;
  //}}}

  function clean_str(str) {
    return str.replace(reg_btag, '');
  }

  function initPre(node) {
    initPre = null;
    var css = {
      position: 'absolute',
      left: -9999,
      width: node.width() + 'px',
      'font-family': node.css('font-family'),
      'font-size': node.css('font-size'),
      'word-wrap': 'break-word',
      border: '1px'
    };

    pre = $('<pre id="douban_pre"></pre>').css(css).appendTo('body');
  };

  //{{{
  var utils = {
    // highlight tagged name
    highlight: function(data, txt, leadChar) {
      leadChar = leadChar || '@';
      var arr = [];

      for (var name in data) {
        arr.push([name, data[name]]);
      }
      // ä¿è¯å…ˆæ›¿æ¢é•¿çš„ç”¨æˆ·å ä»¥è§£å†³é•¿ååŒ…å«çŸ­åçš„æƒ…å†µ
      arr.sort(function(a, b) {
        return a[0].length < b[0].length;
      });

      $.each(arr, function(i, item) {
        var name = item[0];
        var uid = item[1];
        if (ie_old) name = name.replace(reg_space, '&nbsp;');

        txt = txt.replace(new RegExp(leadChar + name.replace(reg_regchar, '\\$1'), 'g'),
        '<code data-id="' + uid + '">' + leadChar + name + '</code>');
      });

      return txt;
    },
    escape_html: function(txt) {
      return txt.replace(reg_lt, '&lt;').replace(reg_gt, '&gt;');
    },

    // using keyboard in mention list
    moveSelectedItem: function(step, idx) {
      var items = node_suglist.find('li');
      var itemsSize = items.length;

      if (!itemsSize) { return; }

      if (!idx) {
        // index of selected item
        idx = node_suglist.find('.on').index();
        idx += step;

        if (idx >= itemsSize) {
          idx -= itemsSize;
        }

        if (idx < 0) {
          // for only one item
          if (idx === -2) {
            idx = -1;
          }
          idx += itemsSize;
        }
      }

      items.removeClass('on');
      $(items[idx]).addClass('on').find('a').focus();
    },

    getCursorPosition: function(t) {
      if (document.selection) {
        //t.focus();

        var val = t.value;
        var r = t._saved_range || document.selection.createRange();
        var tr = t.createTextRange();
        var tr2 = tr.duplicate();
        tr2.moveToBookmark(r.getBookmark());
        tr.setEndPoint('EndToStart', tr2);
        if (r == null || tr == null) return val.length;

        //for some reason IE doesn't always count the \n and \r in length
        var text_part = r.text.replace(/[\r\n]/g, '.');
        var text_whole = val.replace(/[\r\n]/g, '.');

        return text_whole.indexOf(text_part, tr.text.length);
      } else {
        return t.selectionStart;
      }
    },

    setCursorPosition: function(t, p) {
      this.selectRangeText(t, p, p);
    },

    selectRangeText: function(t, s, z) {
      if (document.selection) {
        var range = t.createTextRange();

        range.moveEnd('character', -t.value.length);
        range.moveEnd('character', z);
        range.moveStart('character', s);
        range.select();

      } else {
        t.focus();
        t.setSelectionRange(s, z);
      }
    }
  };
  //}}}

  function TagSug(textarea, options) {//{{{
    var self = this;
    self.elem = textarea;
    self.options = options;
    self.tagged = {};
    self.init(options);
    return self;
  }

  TagSug.prototype = {
    on: function(evt, fn) {
      var self = this;
      evt = evt + self.uuid;
      self.node.bind(evt, function(e, data) {
        data = [e].concat(data);
        fn.apply(self, data);
      });
    },
    emit: function(evt) {
      var args = arguments;
      evt = evt + this.uuid;
      data = Array.prototype.slice.call(args, 1);
      this.node.trigger(evt, data);
    },
    init: function(options) {
      activeLeads++;

      var self = this;
      // self.url = options.url;
      // if (options.max) {
      //   self.url = self.url.replace('{max}', options.max);
      // }
      var elem = self.elem;
      var node = $(elem);
      var canTag = true;

      self.uuid = $.uuid++;
      self.node = node;

      node.bind('keyup input propertychange', function(e) {
        // for IE
        if (e.type == 'propertychange' && e.originalEvent.propertyName !== 'value') return;

        var elem = this;
        // cannot input anymore
        if (elem._closed) return self.clearHighligher();

        var is_change_event = !e.keyCode;

        // don't update the `input` after a keyup
        if (is_change_event && !elem._from_change) {
          elem._from_change = true;
          return;
        }

        // if not from
        if (is_change_event) {
          elem._from_change = true;
        } else {
          elem._from_change = false;
        }


        var slices = self._slices = self.slices();
        var val = slices[0];
        var offset = slices[4];

        var hasNoLead = val.indexOf(self.options.leadChar) == -1;

        var canUpdate =  (hasNoLead && self._highlighted) || (!hasNoLead && canTag);

        // suppose you are doing brownian movement
        if (offset < val.length + 1 && canUpdate) {
          self.updateHighlight();
        }


        // do query when not pressing down
        // 'shift' 'up' 'down' 'enter' or 'tab'
        if (!hasNoLead && (is_change_event || [38, 40, 13, 16, 9].indexOf(e.keyCode) == -1)) {
          if (self.options.delay) {
            self.clearTimeout();
            self._t_query = setTimeout(function() {
              slices = self._slices = self.slices();
              self.query(slices);
            }, self.options.delay);
          } else {
            self.query(slices);
          }
        }
        if (hasNoLead) {
          setTimeout(function() {
            if (!activeLeads) self.hideSug();
          }, 200);
          activeLeads--;
        } else {
          activeLeads++;
        }

        if (is_change_event) return;

        var wantGo = (e.keyCode === 9 || e.keyCode === 13);
        var crt = node_suglist && node_suglist.find('.on');
        var hasOn = crt.length && node_suglist.is(':visible');

        if (wantGo && hasOn) self.choose(crt, slices);
      });

      node.bind('keydown', function(e) {
        var keyCode = e.keyCode;
        var is_empty_input = [16,17,18,20,27,33,34,35,36,37,38,39,40,144].indexOf(keyCode) != -1;

        // prevent 'ctrl|command + a' && 'shift + left|right'
        if (
          is_empty_input ||
          (e.ctrlKey || e.metaKey) && keyCode === 65 ||
          e.shiftKey && (keyCode === 37 || keyCode === 39)
          ) {
          canTag = false;
        } else {
          canTag = true;
        }

        // backspace
        if (keyCode == 8) {
          var slices = self.slices();
          var tag = slices[2];
          if (tag && tag in self.tagged) {
            // remove tagged
            elem.value = slices[1] + slices[3];
            delete self.tagged[tag];
            self.setCursor(slices[4] - tag.length - 1);
          }
          self.hideSug();
          return;
        }
      });

      if (!node[0]._sug_ev_binded) {
        node.bind('keydown', function(e) {
          if (!node_suglist || !node_suglist.is(':visible') || !node_suglist.find('ul').length) return;

          switch (e.keyCode) {
          // space
          case 32:
            self.hideSug();
            break;

            // up
          case 38:
            e.preventDefault();
            utils.moveSelectedItem(-1);
            break;

            // down
          case 40:
            e.preventDefault();
            utils.moveSelectedItem(1);
            break;

            // tab
          case 9:
            e.preventDefault();
            break;

            // enter
          case 13:
            e.preventDefault();
            var a = node_suglist.find('li.on').find('a')[0];
            if (a && !a.id && a.href) {
              a.click();
            }
            break;

          }
        });
        node[0]._sug_ev_binded = true;
      }
    },
    clearTimeout: function() {
      try {
        clearTimeout(this._t_query);
      } catch (e) {}
    },

    // get slices according to current cursor position
    slices: function() {
      var self = this,
      elem = self.elem, val = elem.value,
      offset = self.getCursor(),
      anterior = val.slice(0, offset),
      tail = val.slice(offset),
      last_leadChar_pos = anterior.lastIndexOf(this.options.leadChar);

      if (last_leadChar_pos == -1) {
        return [val, anterior, null, tail, offset];
      }

      var pre = anterior.slice(0, last_leadChar_pos),
      // the `tag` does not contains the leadChar
      tag = anterior.slice(last_leadChar_pos + 1);

      return [val, pre, tag, tail, offset];
    },

    getCursor: function() {
      return utils.getCursorPosition(this.elem);
    },
    setCursor: function(p) {
      return utils.setCursorPosition(this.elem, p);
    },

    updateHighlight: function() {
      var self = this;
      if (!self.options.highlight) return;


      var elem = self.elem;
      var txt = utils.escape_html(elem.value);
      if (ie_old) txt = txt.replace(reg_space, blank_char);
      var high_txt = utils.highlight(self.tagged, txt, self.options.leadChar);
      if (high_txt != txt) self._highlighted = true;
      else self._highlighted = false;
      var hi = $(self.options.highlighter);
      hi.html(high_txt);
      hi.css('marginTop', - elem.scrollTop);
    },

    // replace screenName in val, return uid
    cleanVal: function(val) {
      var end_val = val || '';
      var tagged = this.tagged;

      var name;
      var names = [];
      for (name in tagged) {
        names.push(name.replace(reg_regchar, '\\$1'));
      }

      if (!names.length) return end_val;

      names.sort(function(a, b) { return a.length < b.length });
      names = names.join('|');
      end_val = end_val.replace(new RegExp('@(' + names + ')', 'g'), function(p0, p1) {
        return '@' + tagged[p1];
      });

      return end_val;
    },

    choose: function(item, slices) {
      var self = this;

      self.hideSug();

      var elem = self.elem;
      var val = elem.value;
      if (!item) item = node_suglist.find('.on');
      if (!slices) slices = self._slices || self.slices();
      var tag = slices[2] || '';

      var uid = clean_str(item.attr('data-id') || item.attr('id'));

      if (!uid) return;

      var screenName = uid;
      // show screen name instead of uid (default)
      // and it's your responsibility to handle submit event
      if (!self.options.useUid) {
        screenName = $.trim(item.text().split('(')[0]);
        if (
          screenName.indexOf(self.options.leadChar) > -1 ||
          //reg_specialChars.test(screenName) ||
          // if we encountered people with same name
          node_suglist.text().split(screenName + '(').length > 3
          ) {
          screenName = uid;
        }
      }

      self.emit('choose', screenName, uid);

      // store taged
      var tagged = this.tagged;
      tagged[screenName] = clean_str(uid);

      // slices = [val, pre, tag, tail, offset]
      elem.value = slices[1] + self.options.leadChar +
      screenName + ' ' + slices[3];

      var offset = slices[4] - tag.length + screenName.length + 1;

      self.setCursor(offset);
      self.updateHighlight();
      self._is_waiting = false;
    },

    showSug: function(data) {
      var self = this;
      if (!data) {
        self.hideSug();
        return self;
      }

      if ('_autocomplete' in self) {
        self._autocomplete = self.node.attr('autocomplete');
      }

      self.node.attr('autocomplete', 'off');

      var html = (typeof data == 'string') ?
      '<div class="bd">' + data + '</div>' :
      Mustache.to_html(this.options.listTmpl || '', data);

      node_suglist.crtApi = this;
      self.emit('show', data);

      var doc_www = $(document).width(),
          doc_hhh = $(document).height();

      showSug(html, self.getSugPos());

      var list = $('#db-tagsug-list'),
          tooooop = list.offset().top,
          leeeeft = list.offset().left,
          win_www = $(window).width(),
          win_hhh = $(window).height(),
          ele_www = list.width(),
          ele_hhh = list.height();

      // alert(leeeeft)
      // alert(ele_www)
      // alert(doc_www)
          // alert(tooooop)
          // alert(ele_hhh)
          // alert(ele_hhh)
          if(leeeeft + ele_www > doc_www) {
              $('#db-tagsug-list').css({
                  'left': doc_www - ele_www - 20
              })
          }
          if( tooooop + ele_hhh > doc_hhh) {
              $('#db-tagsug-list').css({
              // 'top':'auto',
                  'top' : doc_hhh - ele_hhh - 20
              })
          } 

      // select first item
      if (!node_suglist.find('li').hasClass('on')) {
        node_suglist.find('li:first').addClass('on');
      }
      return self;
    },

    hideSug: function() {
      var self = this;
      self.node.attr('autocomplete', self._autocomplete);
      self.emit('hide');
      hideSug();
      return self;
    },

    query: function(slices) {
      var self = this;
      var options = self.options;
      var elem = self.elem;

      if (!slices) slices = self.slices();

      var val = slices[0];
      var tag = slices[2];
      self._anterior_txt = slices[1] + (tag || '');

      var customData = options.customData;
      var mode = options.mode;
      var max = options.max;
      var listTmpl = options.listTmpl;
      var arrName = options.arrName;

      // cannot do the query
      if (tag === null || tag.length > self.options.wordLimit || tag.indexOf(' ') != -1) return self.hideSug();

      // try to retrive the customData
      if (typeof customData == 'function') {
        customData = customData();
      }

      // empty keyword means we are right after the leadChar
      if (tag === '') {
        var list = customData && customData[arrName];
        if (!list || !list.length) return self.showSug(self.options.tips);

        return self.showSug(customData);
      }
      customData && (customData.q = tag);
      if (!self.url) return self.showSug(customData);

      self.emit('query', tag);
      self._is_waiting = true;

      // containing char '@' but not 'space'
      $.getJSON(self.url + encodeURIComponent(tag), function(o) {
        if (!self._is_waiting) return;

        if (!o) o = {};
        if (!o[arrName]) o[arrName] = [];

        // not enough
        var list = o[arrName];
        var item = list[0];
        var excludes = {};
        if (item && (item.uid || item.id)) {
          $.each(list, function(i, item) {
            var id = item.id = (item.id || clean_str(item.uid));
            id && (excludes[id] = 1);
          });
        }
        if (list.length < max && typeof options.customData == 'function') {
          list = o[arrName] = list.concat(options.customData(tag, max - list.length, excludes)[arrName]);
        }

        if (!list.length) return self.hideSug();

        // render suggest list
        self.showSug(o);
      });
    },

    // for complete mode
    getSugPos: function() {
      var self = this;
      var con = self._anterior_txt;
      con = utils.escape_html(con);
      var node = $(self.elem);
      nodePos = node.offset(),
      dot = $('<em>&nbsp;</em>'),
      pos = {};

      initPre && initPre(node);

      if (ie_old) con = con.replace(reg_space, blank_char);
      pre.html(con).append(dot);
      pos = dot.position();

      var offset = self.options.sugOffset;

      return {
        marginLeft: node.css('paddingLeft'),
        marginTop: node.css('paddingTop'),
        top: pos.top + nodePos.top + offset.top,
        left: pos.left + nodePos.left + offset.left
      };
    }
  };
  //}}}

  var defaults = {
    mode: 'complete',
    // word length limit
    wordLimit: 8,
    // url: 'https://api.douban.com/shuo/in/complete?alt=xd&count={max}&callback=?&word=',
    // url: '/api?alt=xd&count={max}&callback=?&word=',
    // url : null,
    max: 10,
    delay: 200, // milliseconds
    customData: null,
    highlight: false,
    highlighter: '.tag-sug-hi',
    sugOffset: {
      top: 30,
      left: 14
    },
    listTmpl: '<ul class="{{cls}}">{{#users}}<li data-id="{{{uid}}}"><a href="http://www.douban.com/people/{{id}}"><img src="{{{avatar}}}">{{{username}}}&nbsp;<span>({{{uid}}})</span></a></li>{{/users}}</ul>',
    // the collection's name in data returns
    arrName: 'users',
    leadChar: '@',
    haltLink: true //,
    // tips: '@某人，Ta会收到提醒'
  };

  $.fn.tagsug = function(opts) {
    var options = $.extend({}, defaults, opts);

    if (options.highlighter != defaults.highlighter) {
      options.highlight = true;
    }

    var self = this;
    var api = [];

    self.each(function() {
      var instance = new TagSug(this, options);
      api.push(instance);
    });

    self._tagsug_api = api;

    globalInit && globalInit();

    return self;
  };

  function setSug(html) {
    node_suglist.html(html);
  }
  function showSug(html, pos) {
    if (html) node_suglist.html(html);
    if (html != '<ul class=""></ul>') {
      node_suglist.css(pos).show();
    }
  }
  function hideSug() {
    node_suglist.hide();
  }

  var globalInit = function() {
    node_suglist = $('#db-tagsug-list');
    if (!node_suglist.length) {
      node_suglist = $(TMPL_SUGGEST_OVERLAY).appendTo(oBody);
    }

    node_suglist.delegate('li', 'click', function(e) {
      var crtApi = node_suglist.crtApi;
      crtApi && crtApi.choose($(e.currentTarget));
    }).delegate('li', 'hover', function(e) {
      $(e.currentTarget).parent().children('.on').removeClass('on')
      .end().end().toggleClass('on');
    }).delegate('a', 'click', function(e) {
      var crtApi = node_suglist.crtApi;
      crtApi && crtApi.options.haltLink && e.preventDefault();
    }).click(function(e) {
      node_suglist.hide();
    }).keydown(function(e) {
      var crtApi = node_suglist.crtApi;
      switch (e.keyCode) {
      // space
      case 32:
        hideSug();
        crtApi.node.focus();
        break;

        // up
      case 38:
        e.preventDefault();
        utils.moveSelectedItem(-1);
        break;

        // down
      case 40:
        e.preventDefault();
        utils.moveSelectedItem(1);
        break;

        // tab
      case 9:
        e.preventDefault();
        break;

        // enter
      case 13:
        if (crtApi && crtApi.options.haltLink) {
          crtApi.node.focus();
          e.preventDefault();
        }
        break;

      default:
        break;
      }
    });

    globalInit = null;
  };

  $.TagSug = TagSug;
})(jQuery);
