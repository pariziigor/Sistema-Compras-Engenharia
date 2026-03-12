import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import ProjetoCard from '../components/ProjetoCard';
import { motion as Motion } from 'framer-motion';

export default function ControleProjetos() {
  const [projetos, setProjetos] = useState([]);
  const [projetoExpandido, setProjetoExpandido] = useState(null);

  useEffect(() => {
    api.get('/projetos')
       .then(res => setProjetos(res.data))
       .catch(err => console.error(err));
  }, []);

  return (
    <Motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
      <h2 className="text-xl font-semibold mb-6">Controle de Projetos</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 items-start">
        {projetos.map((projeto) => (
          <ProjetoCard 
            key={projeto.codigo_projeto}
            projeto={projeto}
            isExpanded={projetoExpandido === projeto.codigo_projeto}
            onToggle={() => setProjetoExpandido(projetoExpandido === projeto.codigo_projeto ? null : projeto.codigo_projeto)}
          />
        ))}
      </div>
    </Motion.div>
  );
}