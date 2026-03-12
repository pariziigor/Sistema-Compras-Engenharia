import React, { useState, useEffect } from 'react';
import { AlertCircle } from 'lucide-react';
import { api } from '../services/api';
import { motion as Motion } from 'framer-motion';

export default function PainelCompras() {
  const [necessidades, setNecessidades] = useState([]);

  useEffect(() => {
    api.get('/compras/necessidades')
       .then(res => setNecessidades(res.data))
       .catch(err => console.error(err));
  }, []);

  return (
    <Motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
      <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
        <AlertCircle className="text-orange-500" /> Ação Necessária (Falta de Estoque)
      </h2>
      
      <div className="bg-white rounded-lg shadow border border-slate-200 overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200">
              <th className="p-4 font-medium text-slate-600">Material</th>
              <th className="p-4 font-medium text-slate-600">Demanda (Obras)</th>
              <th className="p-4 font-medium text-slate-600">Estoque Atual</th>
              <th className="p-4 font-medium text-slate-600">Pedidos Colocados</th>
              <th className="p-4 font-bold text-red-600">Comprar Agora</th>
            </tr>
          </thead>
          <tbody>
            {necessidades.length === 0 ? (
              <tr><td colSpan="5" className="p-8 text-center text-slate-500">Nenhuma necessidade de compra no momento. Tudo abastecido!</td></tr>
            ) : (
              necessidades.map((item, index) => (
                <tr key={index} className="border-b border-slate-100 hover:bg-slate-50">
                  <td className="p-4 font-medium">{item.codigo_material} - {item.descricao}</td>
                  <td className="p-4">{item.demanda_total_obras}</td>
                  <td className="p-4 text-emerald-600">{item.estoque_atual}</td>
                  <td className="p-4 text-blue-600">{item.pedidos_colocados}</td>
                  <td className="p-4 font-bold text-red-600 bg-red-50/50">{item.necessidade_real_compra}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </Motion.div>
  );
}