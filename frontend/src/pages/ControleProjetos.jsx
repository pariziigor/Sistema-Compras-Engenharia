import React, { useState, useEffect } from 'react';
import { motion as Motion } from 'framer-motion';
import { Search } from 'lucide-react'; 
import { api } from '../services/api';
import ProjetoCard from '../components/ProjetoCard';

export default function ControleProjetos() {
  const [projetos, setProjetos] = useState([]);
  const [projetoExpandido, setProjetoExpandido] = useState(null);
  const [buscaProjeto, setBuscaProjeto] = useState(''); 

  useEffect(() => {
    api.get('/projetos')
       .then(res => setProjetos(res.data))
       .catch(err => console.error(err));
  }, []);

  const projetosFiltrados = projetos.filter((projeto) => 
    projeto.codigo_projeto.toLowerCase().includes(buscaProjeto.toLowerCase())
  );

  return (
    <Motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
        <h2 className="text-xl font-semibold">Controle de Projetos</h2>
        
        <div className="relative w-full md:w-72">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search size={18} className="text-slate-400" />
          </div>
          <input
            type="text"
            placeholder="Buscar por código (ex: L008)..."
            value={buscaProjeto}
            onChange={(e) => setBuscaProjeto(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm text-slate-700 bg-white shadow-sm"
          />
        </div>
      </div>
      
      {projetosFiltrados.length === 0 ? (
        <div className="text-center p-8 bg-white rounded-lg border border-slate-200 text-slate-500 shadow-sm">
          Nenhum projeto encontrado para esta busca.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 items-start">
          {projetosFiltrados.map((projeto) => (
            <ProjetoCard 
              key={projeto.codigo_projeto}
              projeto={projeto}
              isExpanded={projetoExpandido === projeto.codigo_projeto}
              onToggle={() => setProjetoExpandido(projetoExpandido === projeto.codigo_projeto ? null : projeto.codigo_projeto)}
            />
          ))}
        </div>
      )}
    </Motion.div>
  );
}