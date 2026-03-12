import React from 'react';
import { AnimatePresence } from 'framer-motion';
import { Clock, ChevronDown, ChevronUp } from 'lucide-react';
import { motion as Motion } from 'framer-motion';

export default function ProjetoCard({ projeto, isExpanded, onToggle }) {
  return (
    <Motion.div 
      layout
      className={`bg-white rounded-lg shadow-sm border ${projeto.status === 'Alterado' ? 'border-yellow-400' : 'border-slate-200'} overflow-hidden cursor-pointer`}
      onClick={onToggle}
    >
      <div className="p-5 flex justify-between items-start">
        <div>
          <h3 className="text-lg font-bold text-slate-800">Projeto {projeto.codigo_projeto}</h3>
          <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
            <Clock size={12} /> Atualizado: {new Date(projeto.ultima_alteracao).toLocaleDateString('pt-BR')}
          </p>
        </div>
        <span className={`text-xs px-2 py-1 rounded-full font-medium ${
          projeto.status === 'Alterado' ? 'bg-yellow-100 text-yellow-800' : 
          projeto.status === 'Fechado' ? 'bg-slate-100 text-slate-600' : 
          'bg-blue-100 text-blue-800'
        }`}>
          {projeto.status} (v{projeto.versao})
        </span>
      </div>

      <AnimatePresence>
        {isExpanded && (
          <Motion.div 
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="bg-slate-50 px-5 pb-5 border-t border-slate-100 overflow-hidden"
          >
            <h4 className="text-sm font-semibold text-slate-700 pt-4 mb-2">Histórico de Alterações</h4>
            {projeto.historico && projeto.historico.length > 0 ? (
              <ul className="space-y-3">
                {projeto.historico.map((hist, idx) => (
                  <li key={idx} className="text-sm border-l-2 border-blue-400 pl-3">
                    <span className="text-xs text-slate-500 block">{new Date(hist.data_alteracao).toLocaleString('pt-BR')}</span>
                    <span className="text-slate-700">{hist.descricao_mudanca}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-slate-500">Projeto original, sem alterações registradas.</p>
            )}
          </Motion.div>
        )}
      </AnimatePresence>
      
      <div className="bg-slate-50 px-5 py-2 border-t border-slate-100 flex justify-center text-slate-400">
        {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </div>
    </Motion.div>
  );
}