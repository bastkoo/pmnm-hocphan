document.addEventListener('submit', (event) => {
  const message = event.target.dataset.confirm;
  if (message && !window.confirm(message)) event.preventDefault();
});
document.addEventListener('click', (event) => {
  const step = event.target.closest('[data-step]');
  if (step) {
    const input = step.closest('.quantity').querySelector('input');
    if (!input.disabled) {
      const next = Number(input.value) + Number(step.dataset.step);
      input.value = Math.max(Number(input.min), Math.min(Number(input.max), next));
    }
  }
  const row = event.target.closest('tr[data-href]');
  if (row && !event.target.closest('a,button,input')) window.location.href = row.dataset.href;
});
