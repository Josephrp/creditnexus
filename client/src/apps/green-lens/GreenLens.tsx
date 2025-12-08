import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useFDC3 } from '@/context/FDC3Context';
import type { CreditAgreementData, ESGKPITarget } from '@/context/FDC3Context';
import { Leaf, TrendingDown, TrendingUp, AlertTriangle, CheckCircle2, Target, Droplets, Zap, Recycle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, Legend } from 'recharts';

const MOCK_ESG_DATA: ESGKPITarget[] = [
  {
    kpi_type: 'CO2 Emissions',
    target_value: 50000,
    current_value: 42000,
    unit: 'tons CO2/year',
    margin_adjustment_bps: -25,
  },
  {
    kpi_type: 'Renewable Energy Percentage',
    target_value: 60,
    current_value: 72,
    unit: '%',
    margin_adjustment_bps: -15,
  },
  {
    kpi_type: 'Water Usage',
    target_value: 1000000,
    current_value: 1100000,
    unit: 'gallons/year',
    margin_adjustment_bps: 0,
  },
];

function getKPIIcon(kpiType: string) {
  if (kpiType.toLowerCase().includes('co2') || kpiType.toLowerCase().includes('emission')) {
    return <Leaf className="h-5 w-5" />;
  }
  if (kpiType.toLowerCase().includes('renewable') || kpiType.toLowerCase().includes('energy')) {
    return <Zap className="h-5 w-5" />;
  }
  if (kpiType.toLowerCase().includes('water')) {
    return <Droplets className="h-5 w-5" />;
  }
  if (kpiType.toLowerCase().includes('waste') || kpiType.toLowerCase().includes('recycl')) {
    return <Recycle className="h-5 w-5" />;
  }
  return <Target className="h-5 w-5" />;
}

function isTargetMet(kpi: ESGKPITarget): boolean {
  if (kpi.current_value === undefined) return false;
  
  if (kpi.kpi_type.toLowerCase().includes('emission') || 
      kpi.kpi_type.toLowerCase().includes('water') ||
      kpi.kpi_type.toLowerCase().includes('waste') ||
      kpi.kpi_type.toLowerCase().includes('incident')) {
    return kpi.current_value <= kpi.target_value;
  }
  return kpi.current_value >= kpi.target_value;
}

export function GreenLens() {
  const { context, clearContext } = useFDC3();
  const [loanData, setLoanData] = useState<CreditAgreementData | null>(null);
  const [esgTargets, setEsgTargets] = useState<ESGKPITarget[]>([]);

  useEffect(() => {
    if (context?.loan) {
      setLoanData(context.loan);
      
      if (context.loan.esg_kpi_targets && context.loan.esg_kpi_targets.length > 0) {
        setEsgTargets(context.loan.esg_kpi_targets);
      } else if (context.loan.sustainability_linked) {
        setEsgTargets(MOCK_ESG_DATA);
      } else {
        setEsgTargets(MOCK_ESG_DATA);
      }
    }
  }, [context]);

  const handleClear = () => {
    setLoanData(null);
    setEsgTargets([]);
    clearContext();
  };

  const borrower = loanData?.parties?.find(p => p.role.toLowerCase().includes('borrower'));
  
  const totalMarginAdjustment = esgTargets.reduce((sum, kpi) => {
    if (isTargetMet(kpi)) {
      return sum + kpi.margin_adjustment_bps;
    }
    return sum;
  }, 0);

  const targetsMetCount = esgTargets.filter(isTargetMet).length;
  const isSustainabilityLinked = loanData?.sustainability_linked || esgTargets.length > 0;

  const chartData = esgTargets.map(kpi => ({
    name: kpi.kpi_type.split(' ').slice(0, 2).join(' '),
    target: kpi.target_value,
    current: kpi.current_value || 0,
    met: isTargetMet(kpi),
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Leaf className="h-6 w-6 text-emerald-400" />
            GreenLens
          </h2>
          <p className="text-muted-foreground">ESG Performance & Margin Ratchet</p>
        </div>
        {loanData && (
          <button onClick={handleClear} className="text-sm text-muted-foreground hover:text-white">
            Clear Data
          </button>
        )}
      </div>

      {!loanData ? (
        <Card className="border-slate-700 bg-slate-800/50">
          <CardContent className="p-12 text-center">
            <div className="w-20 h-20 rounded-full bg-emerald-500/10 flex items-center justify-center mx-auto mb-6">
              <Leaf className="h-10 w-10 text-emerald-500/50" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Waiting for Loan Context</h3>
            <p className="text-muted-foreground max-w-md mx-auto">
              Use the Docu-Digitizer to extract loan data and broadcast it here.
              ESG performance metrics and margin adjustments will be displayed automatically.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="border-slate-700 bg-slate-800/50">
              <CardContent className="p-4">
                <div className="text-xs text-muted-foreground mb-1">Borrower</div>
                <div className="font-medium truncate">{borrower?.name || 'N/A'}</div>
              </CardContent>
            </Card>
            
            <Card className="border-slate-700 bg-slate-800/50">
              <CardContent className="p-4">
                <div className="text-xs text-muted-foreground mb-1">Sustainability Linked</div>
                <div className="font-medium flex items-center gap-2">
                  {isSustainabilityLinked ? (
                    <>
                      <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                      <span className="text-emerald-400">Yes</span>
                    </>
                  ) : (
                    <span>No</span>
                  )}
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-slate-700 bg-slate-800/50">
              <CardContent className="p-4">
                <div className="text-xs text-muted-foreground mb-1">ESG Targets Met</div>
                <div className="font-medium">
                  <span className="text-emerald-400">{targetsMetCount}</span>
                  <span className="text-muted-foreground"> / {esgTargets.length}</span>
                </div>
              </CardContent>
            </Card>
            
            <Card className={`border-2 ${totalMarginAdjustment < 0 ? 'border-emerald-500/50 bg-emerald-500/10' : 'border-slate-700 bg-slate-800/50'}`}>
              <CardContent className="p-4">
                <div className="text-xs text-muted-foreground mb-1">Total Margin Adjustment</div>
                <div className={`font-bold text-lg flex items-center gap-1 ${totalMarginAdjustment < 0 ? 'text-emerald-400' : 'text-slate-400'}`}>
                  {totalMarginAdjustment < 0 ? (
                    <TrendingDown className="h-4 w-4" />
                  ) : totalMarginAdjustment > 0 ? (
                    <TrendingUp className="h-4 w-4" />
                  ) : null}
                  {totalMarginAdjustment > 0 ? '+' : ''}{totalMarginAdjustment} bps
                </div>
              </CardContent>
            </Card>
          </div>

          {totalMarginAdjustment < 0 && (
            <Card className="border-emerald-500/30 bg-gradient-to-r from-emerald-500/10 to-transparent">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 rounded-full bg-emerald-500/20 flex items-center justify-center">
                    <Leaf className="h-8 w-8 text-emerald-400" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-emerald-400">Margin Discount Applied</h3>
                    <p className="text-muted-foreground">
                      Based on ESG performance, this loan qualifies for a{' '}
                      <span className="text-emerald-400 font-medium">{Math.abs(totalMarginAdjustment)} bps</span> margin reduction.
                    </p>
                  </div>
                  <div className="ml-auto text-right">
                    <div className="text-3xl font-bold text-emerald-400">{totalMarginAdjustment} bps</div>
                    <div className="text-sm text-muted-foreground">Annual Savings</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          <div className="grid lg:grid-cols-2 gap-6">
            <Card className="border-slate-700 bg-slate-800/50">
              <CardHeader>
                <CardTitle>ESG Performance vs Targets</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData} layout="vertical" margin={{ left: 20, right: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis type="number" stroke="#64748b" />
                      <YAxis dataKey="name" type="category" stroke="#64748b" width={80} tick={{ fontSize: 12 }} />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#1e293b', 
                          border: '1px solid #334155',
                          borderRadius: '8px',
                        }}
                      />
                      <Legend />
                      <Bar dataKey="target" name="Target" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                      <Bar dataKey="current" name="Current" radius={[0, 4, 4, 0]}>
                        {chartData.map((entry, index) => (
                          <Cell 
                            key={`cell-${index}`} 
                            fill={entry.met ? '#10b981' : '#f59e0b'} 
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card className="border-slate-700 bg-slate-800/50">
              <CardHeader>
                <CardTitle>KPI Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {esgTargets.map((kpi, idx) => {
                    const met = isTargetMet(kpi);
                    const percentage = kpi.current_value 
                      ? Math.round((kpi.current_value / kpi.target_value) * 100) 
                      : 0;
                    
                    return (
                      <div key={idx} className="p-4 bg-slate-900/50 rounded-lg border border-slate-700">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-2">
                            <div className={`p-2 rounded-lg ${met ? 'bg-emerald-500/20 text-emerald-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                              {getKPIIcon(kpi.kpi_type)}
                            </div>
                            <div>
                              <div className="font-medium">{kpi.kpi_type}</div>
                              <div className="text-xs text-muted-foreground">{kpi.unit}</div>
                            </div>
                          </div>
                          {met ? (
                            <span className="flex items-center gap-1 text-emerald-400 text-sm">
                              <CheckCircle2 className="h-4 w-4" />
                              Target Met
                            </span>
                          ) : (
                            <span className="flex items-center gap-1 text-yellow-400 text-sm">
                              <AlertTriangle className="h-4 w-4" />
                              Below Target
                            </span>
                          )}
                        </div>
                        
                        <div className="grid grid-cols-3 gap-4 text-sm">
                          <div>
                            <div className="text-muted-foreground">Current</div>
                            <div className="font-mono">{kpi.current_value?.toLocaleString() || 'N/A'}</div>
                          </div>
                          <div>
                            <div className="text-muted-foreground">Target</div>
                            <div className="font-mono">{kpi.target_value.toLocaleString()}</div>
                          </div>
                          <div>
                            <div className="text-muted-foreground">Margin Impact</div>
                            <div className={`font-mono ${met && kpi.margin_adjustment_bps < 0 ? 'text-emerald-400' : ''}`}>
                              {met ? `${kpi.margin_adjustment_bps > 0 ? '+' : ''}${kpi.margin_adjustment_bps} bps` : '—'}
                            </div>
                          </div>
                        </div>

                        <div className="mt-3">
                          <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                            <div 
                              className={`h-full transition-all ${met ? 'bg-emerald-500' : 'bg-yellow-500'}`}
                              style={{ width: `${Math.min(percentage, 100)}%` }}
                            />
                          </div>
                          <div className="text-xs text-muted-foreground mt-1 text-right">{percentage}% of target</div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
