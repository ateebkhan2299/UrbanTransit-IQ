import React, { useState } from 'react';
import Header from '../components/Header';
import { exportReport } from '../api/client';
import { FileText, Download, FileSpreadsheet, CheckCircle, AlertCircle } from 'lucide-react';

const REPORT_TYPES = [
  { id: 'passenger_demand', name: 'Passenger Demand & Flow', desc: 'Origin-destination matrices and hourly boarding data.' },
  { id: 'route_performance', name: 'Route Performance', desc: 'Rankings, reliability scores, and overall health.' },
  { id: 'delays', name: 'Delay & Bottlenecks', desc: 'Incident causes, delay severity, and hotspot locations.' },
  { id: 'occupancy', name: 'Occupancy & Crowding', desc: 'Historical utilization rates and overcrowded trips.' },
  { id: 'forecasting', name: 'Demand Forecasting', desc: 'Future predicted volumes and error metrics.' },
  { id: 'route_clustering', name: 'Route Clustering', desc: 'Unsupervised ML clustering of routes by behavior.' },
  { id: 'recommendations', name: 'Actionable Recommendations', desc: 'Model-derived suggestions for schedule optimization.' },
  { id: 'model_comparison', name: 'Spark vs Python Comparison', desc: 'Dual-pipeline validation results and mismatches.' },
];

const ReportsExport = () => {
  const [downloadStatus, setDownloadStatus] = useState(null); // { id: string, type: string, status: 'loading' | 'success' | 'error' }

  const handleDownload = async (reportId, format) => {
    setDownloadStatus({ id: reportId, type: format, status: 'loading' });
    try {
      // Need to tell axios to return a blob
      const res = await exportReport(reportId, format);
      if (res.status === 200) {
        const blob = new Blob([res.data], { type: format === 'csv' ? 'text/csv' : 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `urbantransit_${reportId}_export.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        
        setDownloadStatus({ id: reportId, type: format, status: 'success' });
        setTimeout(() => setDownloadStatus(null), 3000);
      }
    } catch (err) {
      console.error(`Export failed for ${reportId} (${format}):`, err);
      setDownloadStatus({ id: reportId, type: format, status: 'error' });
      setTimeout(() => setDownloadStatus(null), 4000);
    }
  };

  return (
    <div>
      <Header
        title="Reports & Data Export"
        subtitle="Download raw analytics data and formatted management reports"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {REPORT_TYPES.map((report) => (
          <div key={report.id} className="glass-card p-6 flex flex-col justify-between">
            <div className="mb-6">
              <div className="flex items-center gap-3 mb-2">
                <FileText className="w-6 h-6 text-cyan-400" />
                <h3 className="text-lg font-bold text-white">{report.name}</h3>
              </div>
              <p className="text-sm text-slate-400">{report.desc}</p>
            </div>
            
            <div className="flex gap-4">
              <button 
                onClick={() => handleDownload(report.id, 'csv')}
                className="flex-1 flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 py-2 px-4 rounded border border-slate-600 transition-colors"
                disabled={downloadStatus?.id === report.id && downloadStatus?.status === 'loading'}
              >
                {downloadStatus?.id === report.id && downloadStatus?.type === 'csv' ? (
                  downloadStatus.status === 'loading' ? <span className="animate-spin w-4 h-4 border-2 border-slate-400 border-t-transparent rounded-full"></span> :
                  downloadStatus.status === 'success' ? <CheckCircle className="w-4 h-4 text-emerald-400" /> :
                  <AlertCircle className="w-4 h-4 text-red-400" />
                ) : (
                  <>
                    <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
                    CSV Data
                  </>
                )}
              </button>
              
              <button 
                onClick={() => handleDownload(report.id, 'pdf')}
                className="flex-1 flex items-center justify-center gap-2 bg-cyan-900/40 hover:bg-cyan-800/60 text-cyan-100 py-2 px-4 rounded border border-cyan-800 transition-colors"
                disabled={downloadStatus?.id === report.id && downloadStatus?.status === 'loading'}
              >
                {downloadStatus?.id === report.id && downloadStatus?.type === 'pdf' ? (
                  downloadStatus.status === 'loading' ? <span className="animate-spin w-4 h-4 border-2 border-cyan-400 border-t-transparent rounded-full"></span> :
                  downloadStatus.status === 'success' ? <CheckCircle className="w-4 h-4 text-emerald-400" /> :
                  <AlertCircle className="w-4 h-4 text-red-400" />
                ) : (
                  <>
                    <Download className="w-4 h-4 text-cyan-400" />
                    PDF Report
                  </>
                )}
              </button>
            </div>
            
            {/* Error Message Tooltip-style */}
            {downloadStatus?.id === report.id && downloadStatus?.status === 'error' && (
              <div className="mt-3 text-xs text-red-400 text-center font-bold">
                Export failed. Please try again.
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ReportsExport;
