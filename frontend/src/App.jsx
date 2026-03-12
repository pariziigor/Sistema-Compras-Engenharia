import React, { useState } from 'react';
import Header from './components/Header';
import PainelCompras from './pages/PainelCompras';
import ControleProjetos from './pages/ControleProjetos';
import ModalUpload from './components/ModalUpload';

export default function App() {
  const [abaAtiva, setAbaAtiva] = useState('compras');
  const [modalAberto, setModalAberto] = useState(false);
  const [atualizacaoTrigger, setAtualizacaoTrigger] = useState(0);

  // Essa função força as páginas a buscarem os dados novos na API Python
  const forcarAtualizacaoDasTelas = () => {
    setAtualizacaoTrigger(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 font-sans">
      <Header 
        abaAtiva={abaAtiva} 
        setAbaAtiva={setAbaAtiva} 
        abrirModal={() => setModalAberto(true)} 
      />

      <main className="p-8 max-w-7xl mx-auto">
        {/* Passamos a chave (key) para os componentes. Quando ela muda, o React refaz a requisição. */}
        {abaAtiva === 'compras' && <PainelCompras key={`compras-${atualizacaoTrigger}`} />}
        {abaAtiva === 'projetos' && <ControleProjetos key={`projetos-${atualizacaoTrigger}`} />}
      </main>

      <ModalUpload 
        isOpen={modalAberto} 
        onClose={() => setModalAberto(false)} 
        onUploadSuccess={forcarAtualizacaoDasTelas}
      />
    </div>
  );
}