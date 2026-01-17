/**
 * Simple markdown to HTML converter for basic formatting
 * Reused from main application with minor adjustments for landing site
 */
export function markdownToHtml(markdown: string): string {
  let html = markdown
    // Headers
    .replace(/^# (.*$)/gim, '<h1 class="text-3xl font-bold mb-6 mt-8 text-emerald-400">$1</h1>')
    .replace(/^## (.*$)/gim, '<h2 class="text-2xl font-semibold mb-4 mt-6 text-slate-100 border-b border-slate-700 pb-2">$1</h2>')
    .replace(/^### (.*$)/gim, '<h3 class="text-xl font-semibold mb-3 mt-5 text-slate-200">$1</h3>')
    // Bold
    .replace(/\*\*(.*?)\*\*/gim, '<strong class="text-emerald-300">$1</strong>')
    // Italic
    .replace(/\*(.*?)\*/gim, '<em class="text-slate-300">$1</em>')
    // Code blocks
    .replace(/```([\s\S]*?)```/gim, '<pre class="bg-slate-900/50 border border-slate-700 p-4 rounded-lg overflow-x-auto my-6 text-slate-300"><code>$1</code></pre>')
    // Inline code
    .replace(/`([^`]+)`/gim, '<code class="bg-slate-800 px-1.5 py-0.5 rounded text-sm text-emerald-300">$1</code>')
    // Links
    .replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2" class="text-emerald-400 hover:text-emerald-300 transition-colors underline" target="_blank" rel="noopener noreferrer">$1</a>')
    // Lists
    .replace(/^\* (.*$)/gim, '<li class="ml-4 mb-2">$1</li>')
    .replace(/^- (.*$)/gim, '<li class="ml-4 mb-2">$1</li>')
    .replace(/^(\d+)\. (.*$)/gim, '<li class="ml-4 mb-2">$2</li>')
    // Paragraphs
    .split('\n\n')
    .map(para => {
      if (para.trim().startsWith('<')) {
        return para; // Already formatted
      }
      return `<p class="mb-5 leading-relaxed text-slate-300">${para.trim()}</p>`;
    })
    .join('\n');

  // Wrap list items in ul tags
  html = html.replace(/(<li[^>]*>.*<\/li>)/gim, (match) => {
    if (!match.includes('<ul')) {
      return `<ul class="list-disc ml-6 mb-6 space-y-1 text-slate-300">${match}</ul>`;
    }
    return match;
  });

  return html;
}
