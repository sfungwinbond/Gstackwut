const measured = new Map();
const elements = [...document.querySelectorAll('[data-pretext]')];

async function applyPretext() {
  if (!elements.length) return;
  try {
    const { prepare, layout } = await import('https://esm.sh/@chenglou/pretext');
    await document.fonts.ready;
    const prepareElement = (element) => {
      const style = getComputedStyle(element);
      measured.set(element, { handle: prepare(element.textContent, style.font), lineHeight: Number.parseFloat(style.lineHeight) });
    };
    const relayout = () => measured.forEach(({ handle, lineHeight }, element) => {
      const result = layout(handle, element.clientWidth, lineHeight);
      element.style.minHeight = `${Math.ceil(result.height)}px`;
    });
    elements.forEach((element) => {
      prepareElement(element);
      new MutationObserver(() => { prepareElement(element); relayout(); }).observe(element, { characterData: true, subtree: true, childList: true });
      new ResizeObserver(relayout).observe(element);
    });
    relayout();
  } catch {
    document.documentElement.dataset.pretext = 'css-fallback';
  }
}

applyPretext();
