const search = document.querySelector('[data-pack-search]');
const packs = [...document.querySelectorAll('[data-pack]')];
const groups = [...document.querySelectorAll('[data-pack-group]')];
const filters = [...document.querySelectorAll('[data-pack-filter]')];
const count = document.querySelector('[data-pack-count]');
const empty = document.querySelector('[data-pack-empty]');

let activeCategory = 'all';

function applyFilters() {
  const query = search?.value.trim().toLowerCase() ?? '';
  let visible = 0;

  packs.forEach((pack) => {
    const categoryMatches = activeCategory === 'all' || pack.dataset.category === activeCategory;
    const queryMatches = !query || pack.dataset.search.includes(query);
    const matches = categoryMatches && queryMatches;
    pack.hidden = !matches;
    visible += Number(matches);
  });

  groups.forEach((group) => {
    group.hidden = !group.querySelector('[data-pack]:not([hidden])');
  });

  if (count) count.textContent = `${visible} ${visible === 1 ? 'pack' : 'packs'}`;
  if (empty) empty.hidden = visible !== 0;
}

search?.addEventListener('input', applyFilters);

filters.forEach((filter) => {
  filter.addEventListener('click', () => {
    activeCategory = filter.dataset.packFilter;
    filters.forEach((candidate) => {
      candidate.setAttribute('aria-pressed', String(candidate === filter));
    });
    applyFilters();
  });
});

async function copyText(value) {
  try {
    await navigator.clipboard.writeText(value);
    return true;
  } catch {
    const input = document.createElement('textarea');
    input.value = value;
    input.setAttribute('readonly', '');
    input.style.position = 'fixed';
    input.style.opacity = '0';
    document.body.append(input);
    input.select();
    const copied = document.execCommand('copy');
    input.remove();
    return copied;
  }
}

document.querySelectorAll('[data-copy-command]').forEach((button) => {
  button.addEventListener('click', async () => {
    const original = button.textContent;
    const copied = await copyText(button.dataset.copyCommand);
    button.textContent = copied ? 'Copied' : 'Copy failed';
    window.setTimeout(() => {
      button.textContent = original;
    }, 1600);
  });
});

// FALLBACK: the vendored Pretext bundle is unavailable, so CSS remains the
// source of truth if this optional text-measurement enhancement cannot load.
async function enhanceTextLayout() {
  try {
    const { prepare, layout } = await import('https://esm.sh/@chenglou/pretext');
    await document.fonts.ready;
    const measured = new Map();
    const elements = [...document.querySelectorAll('[data-pretext]')];

    const prepareElement = (element) => {
      const style = getComputedStyle(element);
      measured.set(element, {
        handle: prepare(element.textContent, style.font),
        lineHeight: Number.parseFloat(style.lineHeight),
      });
    };

    const relayout = () => {
      measured.forEach(({ handle, lineHeight }, element) => {
        const result = layout(handle, element.clientWidth, lineHeight);
        element.style.setProperty('--measured-height', `${Math.ceil(result.height)}px`);
      });
    };

    elements.forEach((element) => {
      prepareElement(element);
      new ResizeObserver(relayout).observe(element);
    });
    relayout();
    document.documentElement.dataset.pretext = 'ready';
  } catch {
    document.documentElement.dataset.pretext = 'css-fallback';
  }
}

enhanceTextLayout();
