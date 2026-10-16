// Minimal stand-in for the Design runtime: enough to preview .dc.html artboards for review.
(function () {
  const xdc = document.querySelector('x-dc');
  const helmet = xdc.querySelector('helmet');
  if (helmet) { Array.from(helmet.children).forEach((n) => document.head.appendChild(n.cloneNode(true))); helmet.remove(); }
  const tpl = document.createElement('div');
  Array.from(xdc.childNodes).forEach((n) => tpl.appendChild(n.cloneNode(true)));
  xdc.style.display = 'none';
  const host = document.createElement('div');
  document.body.appendChild(host);

  const src = document.querySelector('script[data-dc-script]').textContent;
  class DCLogic {
    constructor(props) { this.props = props || {}; this.state = null; }
    setState(s) { this.state = Object.assign({}, this.state || {}, s); render(); }
  }
  const Component = new Function('DCLogic', src + '\n;return Component;')(DCLogic);
  const inst = new Component({});

  const HOLE = /\{\{\s*([^}]+?)\s*\}\}/g;
  const resolve = (expr, scope) => {
    expr = expr.trim();
    if (expr === 'true') return true; if (expr === 'false') return false;
    if (/^-?\d+(\.\d+)?$/.test(expr)) return Number(expr);
    return expr.split('.').reduce((o, k) => (o == null ? undefined : o[k]), scope);
  };
  const single = (s) => { const m = /^\s*\{\{\s*([^}]+?)\s*\}\}\s*$/.exec(s); return m ? m[1] : null; };

  function proc(node, scope) {
    if (node.nodeType === 3) { node.textContent = node.textContent.replace(HOLE, (_, e) => { const v = resolve(e, scope); return v == null ? '' : String(v); }); return; }
    if (node.nodeType !== 1) return;
    const tag = node.tagName.toLowerCase();
    if (tag === 'sc-for') {
      const list = resolve(single(node.getAttribute('list')), scope) || [];
      const as = node.getAttribute('as');
      const frag = document.createDocumentFragment();
      list.forEach((item, i) => {
        const s = Object.create(scope); s[as] = item; s.$index = i;
        Array.from(node.childNodes).forEach((c) => { const k = c.cloneNode(true); frag.appendChild(k); proc(k, s); });
      });
      node.replaceWith(frag); return;
    }
    if (tag === 'sc-if') {
      const v = resolve(single(node.getAttribute('value')), scope);
      if (!v) { node.remove(); return; }
      const frag = document.createDocumentFragment();
      Array.from(node.childNodes).forEach((c) => { frag.appendChild(c); });
      const kids = Array.from(frag.childNodes);
      node.replaceWith(frag); kids.forEach((k) => proc(k, scope)); return;
    }
    Array.from(node.attributes).forEach((a) => {
      if (!a.value.includes('{{')) return;
      const one = single(a.value);
      if (one && a.name.startsWith('on')) {
        const fn = resolve(one, scope); node.removeAttribute(a.name);
        if (typeof fn === 'function') node.addEventListener(a.name.slice(2), fn);
        return;
      }
      const val = one ? resolve(one, scope) : a.value.replace(HOLE, (_, e) => { const v = resolve(e, scope); return v == null ? '' : String(v); });
      node.setAttribute(a.name, val == null ? '' : String(val));
    });
    Array.from(node.childNodes).forEach((c) => proc(c, scope));
  }

  function render() {
    const vals = inst.renderVals();
    const clone = tpl.cloneNode(true);
    proc(clone, vals);
    host.innerHTML = '';
    Array.from(clone.childNodes).forEach((n) => host.appendChild(n));
    host.querySelectorAll('select[value]').forEach((s) => { s.value = s.getAttribute('value'); });
  }
  render();
  window.__dcReady = true;
})();
