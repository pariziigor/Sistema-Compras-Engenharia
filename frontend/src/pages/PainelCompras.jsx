import React, { useState, useEffect } from 'react';
import { motion as Motion } from 'framer-motion';
import { AlertCircle, Search, Download } from 'lucide-react'; 
import { api } from '../services/api';

export default function PainelCompras() {
  const [necessidades, setNecessidades] = useState([]);
  const [termoBusca, setTermoBusca] = useState(''); 

  useEffect(() => {
    api.get('/compras/necessidades')
       .then(res => setNecessidades(res.data))
       .catch(err => console.error(err));
  }, []);

  const necessidadesFiltradas = necessidades.filter((item) => {
    const busca = termoBusca.toLowerCase();
    return (
      item.descricao.toLowerCase().includes(busca) || 
      item.codigo_material.toLowerCase().includes(busca)
    );
  });

  const exportarParaExcel = async () => {
    try {
      const response = await api.get('/compras/exportar', { responseType: 'blob' });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'Relatorio_Compras_Aulevi.xlsx');
      document.body.appendChild(link);
      link.click(); 
      link.parentNode.removeChild(link); 
      
    } catch (error) {
      console.error("Erro ao exportar arquivo:", error);
      alert("Houve um erro ao gerar o relatório. Verifique a conexão com o servidor.");
    }
  };

  return (
    <Motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <AlertCircle className="text-orange-500" /> Ação Necessária (Falta de Estoque)
        </h2>
        
        <div className="flex w-full md:w-auto gap-3">
          <div className="relative w-full md:w-72">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search size={18} className="text-slate-400" />
            </div>
            <input
              type="text"
              placeholder="Buscar material..."
              value={termoBusca}
              onChange={(e) => setTermoBusca(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-sm text-slate-700 bg-white shadow-sm"
            />
          </div>

          <button 
            onClick={exportarParaExcel}
            className="flex items-center justify-center gap-2 bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700 transition-colors shadow-sm text-sm font-medium whitespace-nowrap"
          >
            <Download size={16} /> Exportar Excel
          </button>
        </div>
      </div>
      
      <div className="bg-white rounded-lg shadow border border-slate-200 overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200">
              <th className="p-4 font-medium text-slate-600 w-32">Código</th>
              <th className="p-4 font-medium text-slate-600">Descrição do Material</th>
              <th className="p-4 font-medium text-slate-600 text-center w-16">UN</th>
              <th className="p-4 font-medium text-slate-600 text-center">Demanda (Obras)</th>
              <th className="p-4 font-medium text-slate-600 text-center">Estoque Atual</th>
              <th className="p-4 font-medium text-slate-600 text-center">Pedidos Colocados</th>
              <th className="p-4 font-bold text-red-600 text-center">Comprar Agora</th>
            </tr>
          </thead>
          <tbody>
            {necessidadesFiltradas.length === 0 ? (
              <tr>
                <td colSpan="6" className="p-8 text-center text-slate-500">
                  {termoBusca ? 'Nenhum material encontrado com essa busca.' : 'Nenhuma necessidade de compra no momento. Tudo abastecido!'}
                </td>
              </tr>
            ) : (
              necessidadesFiltradas.map((item, index) => (
                <tr key={index} className="border-b border-slate-100 hover:bg-slate-50">
                  <td className="p-4 font-mono text-sm text-slate-500">{item.codigo_material}</td>
                  <td className="p-4 font-medium text-slate-800">{item.descricao}</td>
                  <td className="p-4 text-center font-semibold text-slate-500">{item.unidade_medida}</td>
                  <td className="p-4 text-center">{item.demanda_total_obras}</td>
                  <td className="p-4 text-center text-emerald-600">{item.estoque_atual}</td>
                  <td className="p-4 text-center text-blue-600">{item.pedidos_colocados}</td>
                  <td className="p-4 text-center font-bold text-red-600 bg-red-50/50">{item.necessidade_real_compra}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </Motion.div>
  );
}