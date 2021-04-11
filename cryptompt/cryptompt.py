# -*- coding: utf-8 -*-
#######################################
#-------------------------------------#
# Module: cryptompt     		      #
#-------------------------------------#
# Creado:			                  #
# 07. 04. 2021                        #
# Ult. modificacion:                  #
# 11. 04. 2021                        #
#-------------------------------------#
# Author: rodmono                     #
#-------------------------------------#
#-------------------------------------#
#-------------------------------------#
#######################################
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys, os
import seaborn as sns
sns.set()
import matplotlib as mpl
import numpy as np
import scipy.optimize as sco

# Global function
def random_weights(n):
    k = np.random.random(n)
    return k / sum(k)
#######################################
#-------------------------------------#
# Portfolio							  #
#-------------------------------------#
#######################################
class Portfolio:

    def __init__( self, weights, data, riskfreerate ):
        self.data     = data.pct_change()[1:]
        self.weights  = weights
        self.mean_ret = self.data.mean()
        self.cov_mat  = self.data.cov()
        self.rfr      = riskfreerate
        self.n_data   = len(data)

        # Results
        self.exp_return = self._expected_return_()
        self.volatility = self._volatility_()
        self.sharpe     = self._sharpe_ratio_()

    def _expected_return_( self ):
        mu = self.mean_ret.dot(self.weights)*self.n_data
        return mu

    def _volatility_( self ):
        sigma = np.sqrt(self.weights.dot(self.cov_mat.dot(self.weights)))*np.sqrt(self.n_data)
        return sigma

    def _sharpe_ratio_( self ):
        sharpe = (self.exp_return-self.rfr)/self.volatility
        return sharpe

    def details( self ):
        aux1 = {'ExpectedReturns': self.exp_return,'Volatility': self.volatility, \
                'SharpeRatio': self.sharpe}
        aux2 = dict(zip(self.data.columns,self.weights))
        aux3 = dict(aux2, **aux1)
        df   = pd.DataFrame(list(aux3.items()), index=[ x for x in range(0,len(list(aux3.items())))])
        df   = df.set_index(0)
        del df.index.name
        return df.T.reset_index(drop=True)

#######################################
#-------------------------------------#
# Monte Carlo Simulation			  #
#-------------------------------------#
#######################################
class MonteCarlo:

    def __init__( self, token_list, data, riskfreerate, n_simulations ):
        self.tkn_list      = token_list
        self.data          = data
        self.rfr           = riskfreerate
        self.n_simulations = n_simulations
        # Do simulation
        self.simulate()

    def _do_simulation_( self ):
        sresults = []
        for i in range(self.n_simulations):
        	w = random_weights(len(self.tkn_list))
        	p = Portfolio(w,self.data,self.rfr)
        	sresults.append(p.details())
        df = pd.concat(sresults).reset_index(drop=True)
        # Convert to DataFrame
        max_sha_port = df.iloc[df['SharpeRatio'].idxmax()]
        min_vol_port = df.iloc[df['Volatility'].idxmin()]
        return df, max_sha_port, min_vol_port

    def simulate( self ):
        r = self._do_simulation_()
        self.simulation_results       = r[0]
        self.max_sharpe_portfolio     = pd.DataFrame(r[1]).T
        self.min_volatility_portfolio = pd.DataFrame(r[2]).T

    def plot( self ):
        # Scatter plot colored by Sharpe Ratio
        fig, ax = plt.subplots(figsize=(10,7))
        self.simulation_results.plot(ax= ax, kind='scatter',x='Volatility', y='ExpectedReturns', c='SharpeRatio', \
                                     cmap='RdYlGn',edgecolors='black', grid=True, label = 'MC Simulation')
        # Maximum Sharpe Ratio
        max_sh = self.max_sharpe_portfolio
        ax.scatter(x=max_sh['Volatility'],y=max_sh['ExpectedReturns'],marker='D',c='r',s=100,label='Maximum Sharpe Ratio')
        # Minimum variance
        min_vol = self.min_volatility_portfolio
        ax.scatter(x=min_vol['Volatility'],y=min_vol['ExpectedReturns'],marker='D',c='b',s=100,label='Minimum Volatility')
        plt.legend()
        ax.set_xlabel('Volatility', fontsize=15)
        ax.set_ylabel('Expected Returns', fontsize=15)
        ax.set_title('Efficient Frontier', fontsize=22)
        plt.show()

    def details( self ):
        max_sh = self.max_sharpe_portfolio
        min_vol= self.min_volatility_portfolio
        aux = max_sh.append(min_vol)
        aux.index = ['MaxSharpe','MinVolatility']
        return aux
#######################################
# END: Simulation					  #
#######################################

import scipy.optimize as sco
#######################################
#-------------------------------------#
# Theory							  #
#-------------------------------------#
#######################################
def _neg_sharpe_ratio_( weights, mean_ret, cov_mat, riskfreerate, len_data ):
    mu    = mean_ret.dot(weights)*len_data
    sigma = np.sqrt(weights.dot(cov_mat.dot(weights)))*np.sqrt(len_data)
    sharpe = (mu-riskfreerate)/sigma
    return -1.*sharpe

def _volatility_( weights, mean_ret, cov_mat, riskfreerate, len_data ):
    sigma = np.sqrt(weights.dot(cov_mat.dot(weights)))*np.sqrt(len_data)
    return sigma

def _expected_return_( weights, mean_ret, cov_mat, riskfreerate, len_data ):
    mu = mean_ret.dot(weights)*len_data
    return mu

class MPTheory:

    def __init__( self, token_list, data, riskfreerate, n_simulations):
        self.tkn_list      = token_list
        self.data          = data
        self.rfr           = riskfreerate
        self.n_simulations = n_simulations

        # Initialize portfolio
        w = random_weights(len(self.tkn_list))
        self.portfolio = Portfolio(w,self.data,self.rfr)

        # Bounds and constraints
        self.constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        self.numAssets   = len(self.tkn_list)
        self.bounds      = tuple( (0,1) for asset in range(self.numAssets))

        # meanReturns, covMatrix, riskFreeRate and data size
        self.args = (self.portfolio.mean_ret.values, self.portfolio.cov_mat.values, self.rfr, len(self.data))

        # Solve system
        self.simulate()

    def max_sharpe( self ):
        opts = sco.minimize(_neg_sharpe_ratio_, self.numAssets*[1./self.numAssets,], args=self.args, method='SLSQP', \
                            bounds=self.bounds, constraints=self.constraints)
        max_sh = opts['x']
        x = dict(zip(self.tkn_list,max_sh))
        return Portfolio(max_sh,self.data, self.rfr).details()


    def min_volatility( self ):
        opts = sco.minimize(_volatility_, self.numAssets*[1./self.numAssets,], args=self.args, method='SLSQP', \
                            bounds=self.bounds, constraints=self.constraints)
        min_vol = opts['x']
        x = dict(zip(self.tkn_list,min_vol))
        return Portfolio(min_vol,self.data, self.rfr).details()

    def efficient_return( self, target ):
        def prt_return(weights):
            return _expected_return_(weights, self.portfolio.mean_ret.values, self.portfolio.cov_mat.values, self.rfr, len(self.data))
        constraints = ({'type': 'eq', 'fun': lambda x: prt_return(x) - target},
                       {'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        opts = sco.minimize(_volatility_, self.numAssets*[1./self.numAssets,], args=self.args, method='SLSQP', \
                            bounds=self.bounds, constraints=constraints)
        return opts

    def efficient_frontier( self ):
        efficientPortfolios = []
        target_returns      = np.linspace(0, 5, self.n_simulations)
        for tret in target_returns:
        	efficientPortfolios.append(self.efficient_return(tret))
        x = np.array([p['fun'] for p in efficientPortfolios])
        df = pd.DataFrame({'Volatility':x, 'ExpectedReturns':target_returns})
        return df.dropna().reset_index(drop=True)

    def simulate( self ):
        self.simulation_results       = self.efficient_frontier()
        self.max_sharpe_portfolio     = self.max_sharpe()
        self.min_volatility_portfolio = self.min_volatility()

    def plot( self ):
        df = self.simulation_results
        df.Volatility = np.round(df.Volatility,6)
        df['aux'] = df.Volatility.diff()
        df = df.loc[df.aux != 0][['Volatility','ExpectedReturns']]
        df = df.loc[df.ExpectedReturns != 0.0]
        df = df.loc[df.ExpectedReturns != df.ExpectedReturns.min()]
        max_sh = self.max_sharpe_portfolio
        min_vol= self.min_volatility_portfolio
        # Scatter plot colored by Sharpe Ratio
        fig, ax = plt.subplots(figsize=(10,7))
        df.plot(ax= ax, kind='scatter',x='Volatility', y='ExpectedReturns', c=df.ExpectedReturns.values.reshape(1,-1), edgecolors='black', \
                grid=True, label = 'Theory')
        # Maximum Sharpe Ratio
        ax.scatter(x=max_sh['Volatility'],y=max_sh['ExpectedReturns'],marker='o',c='r',s=100,label='Maximum Sharpe Ratio')
        # Minimum variance
        ax.scatter(x=min_vol['Volatility'],y=min_vol['ExpectedReturns'],marker='o',c='b',s=100,label='Minimum Volatility')
        plt.legend()
        ax.set_xlabel('Volatility', fontsize=15)
        ax.set_ylabel('Expected Returns', fontsize=15)
        ax.set_title('Efficient Frontier', fontsize=22)
        plt.show()

    def details( self ):
        max_sh = self.max_sharpe_portfolio
        min_vol= self.min_volatility_portfolio
        aux = max_sh.append(min_vol)
        aux.index = ['MaxSharpe','MinVolatility']
        return aux
#######################################
# END: Theory 						  #
#######################################

class RationalPortFolio:

    def __init__( self, token_list, data, riskfreerate, n_simulations, risk_preference = []):
        self.simulation = MonteCarlo(token_list, data, riskfreerate, n_simulations)
        self.theory     = MPTheory(token_list, data, riskfreerate, n_simulations/10)
        self.risk_preference = risk_preference

    def details( self ):
        sim = self.simulation.details()
        sim.index = ['sMaxSharpe','sMinVolatility']
        the = self.theory.details()
        the.index = ['tMaxSharpe','tMinVolatility']
        return sim.append(the)

    def results( self ):
        x = self.details().T
        x['MaxSharpe']     = 0.5*(x['sMaxSharpe'] + x['tMaxSharpe'])
        x['MinVolatility'] = 0.5*(x['sMinVolatility'] + x['tMinVolatility'])
        return x[['MaxSharpe','MinVolatility']].T

    def recommendation( self ):
        try:
            x = self.results().T
            ll = self.risk_preference
            x['Recommendation'] = ll[0]*x.MaxSharpe + ll[1]*x.MinVolatility
            return x[['Recommendation']].T
        except:
            print('Please provide a valid risk preference...')

    def plot( self ):
        fig, ax = plt.subplots(figsize=(10,7))
        # Simulation
        df = self.simulation.simulation_results
        df.plot(ax= ax, kind='scatter',x='Volatility', y='ExpectedReturns', c='SharpeRatio', cmap='RdYlGn', edgecolors='black', \
                grid=True, label = 'MC Simulation',alpha=0.5)
        # Theory
        df = self.theory.simulation_results
        df.Volatility = np.round(df.Volatility,6)
        df['aux'] = df.Volatility.diff()
        df = df.loc[df.aux != 0][['Volatility','ExpectedReturns']]
        df = df.loc[df.ExpectedReturns != 0.0]
        df = df.loc[df.ExpectedReturns != df.ExpectedReturns.min()]
        df.plot(ax= ax, kind='scatter',x='Volatility', y='ExpectedReturns', c=df.ExpectedReturns.values.reshape(1,-1), edgecolors='black', \
                grid=True, label = 'Theory')
        res    = self.results()
        max_sh = res.loc['MaxSharpe']
        min_vol= res.loc['MinVolatility']
        # Maximum Sharpe Ratio
        ax.scatter(x=max_sh['Volatility'],y=max_sh['ExpectedReturns'],marker='o',c='r',s=100,label='Maximum Sharpe Ratio')
        # Minimum variance
        ax.scatter(x=min_vol['Volatility'],y=min_vol['ExpectedReturns'],marker='o',c='b',s=100,label='Minimum Volatility')
        # if there is a Recommendation
        if self.risk_preference != []:
            rec    = self.recommendation()
            # Maximum Sharpe Ratio
            ax.scatter(x=rec['Volatility'],y=rec['ExpectedReturns'],marker='x',c='black',s=100,label='Recommendation')
        plt.legend(loc=7)
        ax.set_xlabel('Volatility (Std. Deviation)', fontsize=15)
        ax.set_ylabel('Expected Returns', fontsize=15)
        ax.set_title('Efficient Frontier', fontsize=22)
        plt.show()
