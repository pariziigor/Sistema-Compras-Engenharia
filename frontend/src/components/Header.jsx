import React from 'react';
import { Package, FolderKanban, UploadCloud } from 'lucide-react';

export default function Header({ abaAtiva, setAbaAtiva, abrirModal }) {
  return (
    <header className="bg-white shadow-sm border-b border-slate-200 px-8 py-4 flex justify-between items-center">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Suprimentos Aulevi</h1>
        <p className="text-sm text-slate-500">Gestão de Demandas de Engenharia</p>
      </div>
      
      <div className="flex gap-4 items-center">
        <div className="flex gap-2 bg-slate-100 p-1 rounded-lg mr-4">
          <button 
            onClick={() => setAbaAtiva('compras')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors text-sm font-medium ${abaAtiva === 'compras' ? 'bg-white shadow-sm text-blue-600' : 'text-slate-500 hover:text-slate-800'}`}
          >
            <Package size={16} /> Compras
          </button>
          <button 
            onClick={() => setAbaAtiva('projetos')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors text-sm font-medium ${abaAtiva === 'projetos' ? 'bg-white shadow-sm text-blue-600' : 'text-slate-500 hover:text-slate-800'}`}
          >
            <FolderKanban size={16} /> Engenharia
          </button>
        </div>

        <button 
          onClick={abrirModal}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors shadow-sm text-sm font-medium"
        >
          <UploadCloud size={16} /> Importar Dados
        </button>
      </div>
    </header>
  );
}