import React, { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { X, UploadCloud, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { api } from '../services/api';
import { motion as Motion } from 'framer-motion';

export default function ModalUpload({ isOpen, onClose, onUploadSuccess }) {
  const [status, setStatus] = useState({ tipo: '', mensagem: '', loading: false });

  const handleUpload = async (tipo, endpoint, idInput) => {
    const input = document.getElementById(idInput);
    const arquivo = input.files[0];

    if (!arquivo) {
      setStatus({ tipo: 'erro', mensagem: 'Por favor, selecione um arquivo primeiro.', loading: false });
      return;
    }

    setStatus({ tipo: 'info', mensagem: `Enviando planilha de ${tipo}...`, loading: true });
    
    const formData = new FormData();
    formData.append('file', arquivo);

    try {
      const response = await api.post(endpoint, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setStatus({ tipo: 'sucesso', mensagem: response.data.mensagem || 'Upload concluído!', loading: false });
      input.value = '';
      
      if (onUploadSuccess) onUploadSuccess();
      
    } catch (error) {
      setStatus({ 
        tipo: 'erro', 
        mensagem: error.response?.data?.detail || 'Erro ao enviar o arquivo.', 
        loading: false 
      });
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center z-50 px-4">
        <Motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="bg-white rounded-xl shadow-xl w-full max-w-lg overflow-hidden"
        >
          <div className="px-6 py-4 border-b border-slate-200 flex justify-between items-center bg-slate-50">
            <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
              <UploadCloud size={20} className="text-blue-600"/> Importar Dados
            </h3>
            <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
              <X size={20} />
            </button>
          </div>

          <div className="p-6 space-y-6">
            
            {/* Bloco 1: Upload de Estoque */}
            <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
              <h4 className="font-semibold text-slate-700 mb-1">Posição de Estoque (Suprimentos)</h4>
              <p className="text-xs text-slate-500 mb-3">Colunas: codigo_material, descricao, quantidade_estoque, quantidade_comprada</p>
              <div className="flex gap-2">
                <input type="file" id="fileEstoque" accept=".xlsx, .xls" className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer" />
                <button 
                  onClick={() => handleUpload('Estoque', '/upload/estoque', 'fileEstoque')}
                  disabled={status.loading}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
                >
                  Enviar
                </button>
              </div>
            </div>

            {/* Bloco 2: Upload da Engenharia */}
            <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
              <h4 className="font-semibold text-slate-700 mb-1">Projetos (Engenharia)</h4>
              <p className="text-xs text-slate-500 mb-3">Colunas: codigo_projeto, codigo_material, quantidade_pedida</p>
              <div className="flex gap-2">
                <input type="file" id="fileEngenharia" accept=".xlsx, .xls" className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-slate-200 file:text-slate-700 hover:file:bg-slate-300 cursor-pointer" />
                <button 
                  onClick={() => handleUpload('Engenharia', '/upload/engenharia', 'fileEngenharia')}
                  disabled={status.loading}
                  className="bg-slate-800 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-slate-900 disabled:opacity-50"
                >
                  Enviar
                </button>
              </div>
            </div>

            {status.mensagem && (
              <div className={`p-4 rounded-md flex items-center gap-3 text-sm ${
                status.tipo === 'sucesso' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' :
                status.tipo === 'erro' ? 'bg-red-50 text-red-800 border border-red-200' :
                'bg-blue-50 text-blue-800 border border-blue-200'
              }`}>
                {status.loading && <Loader2 size={18} className="animate-spin" />}
                {status.tipo === 'sucesso' && <CheckCircle size={18} />}
                {status.tipo === 'erro' && <AlertCircle size={18} />}
                <span>{status.mensagem}</span>
              </div>
            )}
          </div>
        </Motion.div>
      </div>
    </AnimatePresence>
  );
}