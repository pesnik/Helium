'use client';

import { FileExplorer } from '@/components/FileExplorer';

export default function Home() {
  return (
    <main style={{ height: '100vh', width: '100vw', overflow: 'hidden', background: '#202020', color: 'white' }}>
      <FileExplorer />
    </main>
  );
}
