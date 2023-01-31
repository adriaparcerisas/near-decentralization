#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd
import numpy as np
from shroomdk import ShroomDK
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.ticker as ticker
import numpy as np
import altair as alt
sdk = ShroomDK("7bfe27b2-e726-4d8d-b519-03abc6447728")
st.set_page_config(page_title="Near Path to Decentralization", layout="wide",initial_sidebar_state="collapsed")


# In[2]:


st.title('NEAR Path to Decentralization')


# In[3]:


st.markdown('NEAR Protocol uses _Proof-of-Stake (PoS)_ consensus to secure and validate transactions on the blockchain. Validators earn NEAR Token rewards for producing new blocks in the form of a static inflation rate of about 4.5% each year.')
st.markdown('Token holders not interested in being a Validator can stake to a Validator’s staking pool and earn a portion of Token rewards too. This incentivizes Token holders to stay involved with the community and support Validators who are keeping the network running smoothly.')


# In[4]:


st.markdown('One of the main aspects to be aware about the blockchains that use proof of stake is the decentralization. **Decentralization** is by far one of the most important factors in a crypto ecosystem. As you probably already figured out, the validation system in place might fail to honor this by progressively moving towards a more traditional centralized environment. Why and how could this happen? As it was briefly mentioned previously, validators are incentivized to hold more and more NEAR to guarantee a spot in the network for themselves.') 
st.write('Users look at the voting power (= total staked NEAR) of a validator as a good indicator of who to trust and delegate their funds to. This is understandable and that is why there is a need to constantly educate the user base and promote smaller validators.')


# In[30]:


st.markdown('In this dashboard we are gonna asses the state of governance on NEAR in terms of decentralization basing on a different metrics:')
st.write('- Distribution of staking by validators')
st.write('- Power distribution by validator ranks')
st.write('- Most common staking actions currently and over time')
st.write('- Evolution of Nakamoto coefficient')

st.markdown('The major of the aforementioned metrics can be computed to assess both individual validators on NEAR, and validation as a whole. For this reason, in the textbox below you can choose which validator you can analize specifically or if you only want to see the analysis for the whole validators.')

options = ['All', 'Figment', 'Astro-Stakers','Near-Fans','Blockdaemon','Stake1','Zavodil','Legends','Meta-pool','Hashquark',
           'Allnodes','Epic','Stader-Labs','Stakin','Atomic-nodes','Consensus Finoa 00','Staked','Consensus Finoa 01',
           'Openshards','Everstake','Binancenode1']
selected_option = st.selectbox('Choose a validator', options)
st.write('You selected:', selected_option)
st.markdown('_Please consider that it could take a while (up to 2 minute) to load all charts if you selected a different option._')
#st.sidebar.selectbox('Choose a validator', options)


# In[6]:


sql = f"""
SELECT
  trunc(block_timestamp,'day') as date,
  method_name,
  case when method_name in ('deposit_and_stake','stake','stake_all') then 'staking'
  when method_name in ('unstake','unstake_all') then 'unstaking'
  else method_name end as method_name2,
  count(distinct TX_HASH) as actions
from near.core.fact_actions_events_function_call
  WHERE method_name in ('deposit_and_stake','stake','stake_all','unstake','unstake_all','unbond_delegation','update_validator')
  --'vote', 
  and block_timestamp between current_date - INTERVAL '3 MONTHS' and current_date
    group by 1,2,3
  order by 1 asc
"""


# In[7]:

st.experimental_memo(ttl=21600)
@st.cache
def compute(a):
    data=sdk.query(a)
    return data

results = compute(sql)
df = pd.DataFrame(results.records)
df.info()
st.subheader('Main staking activity metrics over the past 3 months')
st.markdown('In this first part, we can take a look at the local government metrics on Near, where it can be seen how the staking actions have been splitted across the protocol, the distribution of validators, the Nakamoto coefficient, as well as some other interesting metrics regarding validators.')


# In[9]:

st.altair_chart(alt.Chart(df, width=1200)
    .mark_bar()
    .encode(x='sum(actions)', y=alt.Y('method_name2',sort='-x'),color=alt.Color('method_name2', scale=alt.Scale(scheme='dark2')))
    .properties(title='Type of action by usage'))


# In[10]:


st.altair_chart(alt.Chart(df, width=1200)
    .mark_bar()
    .encode(x='date:O', y='actions:Q',color=alt.Color('method_name2', scale=alt.Scale(scheme='dark2')))
    .properties(title='Daily actions by type'))

st.write('')


if selected_option == 'Binancenode1':
    sql2 = f"""
    with 
      t1 as (
      SELECT 
        x.block_timestamp as week,
        method_name,
        tx_signer,
        tx_receiver
      FROM near.core.fact_actions_events_function_call x
      JOIN near.core.fact_transactions y ON x.tx_hash = y.tx_hash
      WHERE method_name IN ('deposit_and_stake','unstake_all')
    ),
    t2 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as stakers
      from t1 where method_name='deposit_and_stake'
      group by 1,2
      ),
    t3 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as unstakers
      from t1 where method_name='unstake_all'
      group by 1,2
      )
    SELECT
    ifnull(t2.date,t3.date) as date,
    ifnull(t2.validator,t3.validator) as validator,
    ifnull(stakers,0) as stakerss, ifnull(unstakers*(-1),0) as unstakerss,stakerss+unstakerss as net_stakers
    from t2
    join t3 on t2.date=t3.date and t2.validator=t3.validator where t2.validator not like '%lockup%' and t2.date>=current_date-INTERVAL '3 MONTHS'
    and t2.validator='binancenode1.poolv1.near'
    """
elif selected_option == 'Figment':
    sql2 = f"""
    with 
      t1 as (
      SELECT 
        x.block_timestamp as week,
        method_name,
        tx_signer,
        tx_receiver
      FROM near.core.fact_actions_events_function_call x
      JOIN near.core.fact_transactions y ON x.tx_hash = y.tx_hash
      WHERE method_name IN ('deposit_and_stake','unstake_all')
    ),
    t2 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as stakers
      from t1 where method_name='deposit_and_stake'
      group by 1,2
      ),
    t3 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as unstakers
      from t1 where method_name='unstake_all'
      group by 1,2
      )
    SELECT
    ifnull(t2.date,t3.date) as date,
    ifnull(t2.validator,t3.validator) as validator,
    ifnull(stakers,0) as stakerss, ifnull(unstakers*(-1),0) as unstakerss,stakerss+unstakerss as net_stakers
    from t2
    join t3 on t2.date=t3.date and t2.validator=t3.validator where t2.validator not like '%lockup%' and t2.date>=current_date-INTERVAL '3 MONTHS'
    and t2.validator='figment.poolv1.near'
    """
elif selected_option == 'Astro-Stakers':
    sql2 = f"""
    with 
      t1 as (
      SELECT 
        x.block_timestamp as week,
        method_name,
        tx_signer,
        tx_receiver
      FROM near.core.fact_actions_events_function_call x
      JOIN near.core.fact_transactions y ON x.tx_hash = y.tx_hash
      WHERE method_name IN ('deposit_and_stake','unstake_all')
    ),
    t2 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as stakers
      from t1 where method_name='deposit_and_stake'
      group by 1,2
      ),
    t3 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as unstakers
      from t1 where method_name='unstake_all'
      group by 1,2
      )
    SELECT
    ifnull(t2.date,t3.date) as date,
    ifnull(t2.validator,t3.validator) as validator,
    ifnull(stakers,0) as stakerss, ifnull(unstakers*(-1),0) as unstakerss,stakerss+unstakerss as net_stakers
    from t2
    join t3 on t2.date=t3.date and t2.validator=t3.validator where t2.validator not like '%lockup%' and t2.date>=current_date-INTERVAL '3 MONTHS'
    and t2.validator='astro-stakers.poolv1.near'
    """
         
elif selected_option == 'Near-Fans':
    sql2 = f"""
    with 
      t1 as (
      SELECT 
        x.block_timestamp as week,
        method_name,
        tx_signer,
        tx_receiver
      FROM near.core.fact_actions_events_function_call x
      JOIN near.core.fact_transactions y ON x.tx_hash = y.tx_hash
      WHERE method_name IN ('deposit_and_stake','unstake_all')
    ),
    t2 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as stakers
      from t1 where method_name='deposit_and_stake'
      group by 1,2
      ),
    t3 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as unstakers
      from t1 where method_name='unstake_all'
      group by 1,2
      )
    SELECT
    ifnull(t2.date,t3.date) as date,
    ifnull(t2.validator,t3.validator) as validator,
    ifnull(stakers,0) as stakerss, ifnull(unstakers*(-1),0) as unstakerss,stakerss+unstakerss as net_stakers
    from t2
    join t3 on t2.date=t3.date and t2.validator=t3.validator where t2.validator not like '%lockup%' and t2.date>=current_date-INTERVAL '3 MONTHS'
    and t2.validator='near-fans.poolv1.near'
    """

elif selected_option == 'Blockdaemon':
    sql2 = f"""
    with 
      t1 as (
      SELECT 
        x.block_timestamp as week,
        method_name,
        tx_signer,
        tx_receiver
      FROM near.core.fact_actions_events_function_call x
      JOIN near.core.fact_transactions y ON x.tx_hash = y.tx_hash
      WHERE method_name IN ('deposit_and_stake','unstake_all')
    ),
    t2 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as stakers
      from t1 where method_name='deposit_and_stake'
      group by 1,2
      ),
    t3 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as unstakers
      from t1 where method_name='unstake_all'
      group by 1,2
      )
    SELECT
    ifnull(t2.date,t3.date) as date,
    ifnull(t2.validator,t3.validator) as validator,
    ifnull(stakers,0) as stakerss, ifnull(unstakers*(-1),0) as unstakerss,stakerss+unstakerss as net_stakers
    from t2
    join t3 on t2.date=t3.date and t2.validator=t3.validator where t2.validator not like '%lockup%' and t2.date>=current_date-INTERVAL '3 MONTHS'
    and t2.validator='blockdaemon.poolv1.near'
    """
         
elif selected_option == 'Stake1':
    sql2 = f"""
    with 
      t1 as (
      SELECT 
        x.block_timestamp as week,
        method_name,
        tx_signer,
        tx_receiver
      FROM near.core.fact_actions_events_function_call x
      JOIN near.core.fact_transactions y ON x.tx_hash = y.tx_hash
      WHERE method_name IN ('deposit_and_stake','unstake_all')
    ),
    t2 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as stakers
      from t1 where method_name='deposit_and_stake'
      group by 1,2
      ),
    t3 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as unstakers
      from t1 where method_name='unstake_all'
      group by 1,2
      )
    SELECT
    ifnull(t2.date,t3.date) as date,
    ifnull(t2.validator,t3.validator) as validator,
    ifnull(stakers,0) as stakerss, ifnull(unstakers*(-1),0) as unstakerss,stakerss+unstakerss as net_stakers
    from t2
    join t3 on t2.date=t3.date and t2.validator=t3.validator where t2.validator not like '%lockup%' and t2.date>=current_date-INTERVAL '3 MONTHS'
    and t2.validator='stake1.poolv1.near'
    """
         
elif selected_option == 'Zavodil':
    sql2 = f"""
    with 
      t1 as (
      SELECT 
        x.block_timestamp as week,
        method_name,
        tx_signer,
        tx_receiver
      FROM near.core.fact_actions_events_function_call x
      JOIN near.core.fact_transactions y ON x.tx_hash = y.tx_hash
      WHERE method_name IN ('deposit_and_stake','unstake_all')
    ),
    t2 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as stakers
      from t1 where method_name='deposit_and_stake'
      group by 1,2
      ),
    t3 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as unstakers
      from t1 where method_name='unstake_all'
      group by 1,2
      )
    SELECT
    ifnull(t2.date,t3.date) as date,
    ifnull(t2.validator,t3.validator) as validator,
    ifnull(stakers,0) as stakerss, ifnull(unstakers*(-1),0) as unstakerss,stakerss+unstakerss as net_stakers
    from t2
    join t3 on t2.date=t3.date and t2.validator=t3.validator where t2.validator not like '%lockup%' and t2.date>=current_date-INTERVAL '3 MONTHS'
    and t2.validator='zavodil.poolv1.near'
    """
         
elif selected_option == 'Legends':
    sql2 = f"""
    with 
      t1 as (
      SELECT 
        x.block_timestamp as week,
        method_name,
        tx_signer,
        tx_receiver
      FROM near.core.fact_actions_events_function_call x
      JOIN near.core.fact_transactions y ON x.tx_hash = y.tx_hash
      WHERE method_name IN ('deposit_and_stake','unstake_all')
    ),
    t2 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as stakers
      from t1 where method_name='deposit_and_stake'
      group by 1,2
      ),
    t3 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as unstakers
      from t1 where method_name='unstake_all'
      group by 1,2
      )
    SELECT
    ifnull(t2.date,t3.date) as date,
    ifnull(t2.validator,t3.validator) as validator,
    ifnull(stakers,0) as stakerss, ifnull(unstakers*(-1),0) as unstakerss,stakerss+unstakerss as net_stakers
    from t2
    join t3 on t2.date=t3.date and t2.validator=t3.validator where t2.validator not like '%lockup%' and t2.date>=current_date-INTERVAL '3 MONTHS'
    and t2.validator='legends.poolv1.near'
    """
         
elif selected_option == 'Meta-pool':
    sql2 = f"""
    with 
      t1 as (
      SELECT 
        x.block_timestamp as week,
        method_name,
        tx_signer,
        tx_receiver
      FROM near.core.fact_actions_events_function_call x
      JOIN near.core.fact_transactions y ON x.tx_hash = y.tx_hash
      WHERE method_name IN ('deposit_and_stake','unstake_all')
    ),
    t2 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as stakers
      from t1 where method_name='deposit_and_stake'
      group by 1,2
      ),
    t3 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as unstakers
      from t1 where method_name='unstake_all'
      group by 1,2
      )
    SELECT
    ifnull(t2.date,t3.date) as date,
    ifnull(t2.validator,t3.validator) as validator,
    ifnull(stakers,0) as stakerss, ifnull(unstakers*(-1),0) as unstakerss,stakerss+unstakerss as net_stakers
    from t2
    join t3 on t2.date=t3.date and t2.validator=t3.validator where t2.validator not like '%lockup%' and t2.date>=current_date-INTERVAL '3 MONTHS'
    and t2.validator='meta-pool.near'
    """

elif selected_option == 'Hashquark':
    sql2 = f"""
    with 
      t1 as (
      SELECT 
        x.block_timestamp as week,
        method_name,
        tx_signer,
        tx_receiver
      FROM near.core.fact_actions_events_function_call x
      JOIN near.core.fact_transactions y ON x.tx_hash = y.tx_hash
      WHERE method_name IN ('deposit_and_stake','unstake_all')
    ),
    t2 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as stakers
      from t1 where method_name='deposit_and_stake'
      group by 1,2
      ),
    t3 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as unstakers
      from t1 where method_name='unstake_all'
      group by 1,2
      )
    SELECT
    ifnull(t2.date,t3.date) as date,
    ifnull(t2.validator,t3.validator) as validator,
    ifnull(stakers,0) as stakerss, ifnull(unstakers*(-1),0) as unstakerss,stakerss+unstakerss as net_stakers
    from t2
    join t3 on t2.date=t3.date and t2.validator=t3.validator where t2.validator not like '%lockup%' and t2.date>=current_date-INTERVAL '3 MONTHS'
    and t2.validator='hashquark.poolv1.near'
    """

elif selected_option == 'Allnodes':
    sql2 = f"""
    with 
      t1 as (
      SELECT 
        x.block_timestamp as week,
        method_name,
        tx_signer,
        tx_receiver
      FROM near.core.fact_actions_events_function_call x
      JOIN near.core.fact_transactions y ON x.tx_hash = y.tx_hash
      WHERE method_name IN ('deposit_and_stake','unstake_all')
    ),
    t2 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as stakers
      from t1 where method_name='deposit_and_stake'
      group by 1,2
      ),
    t3 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as unstakers
      from t1 where method_name='unstake_all'
      group by 1,2
      )
    SELECT
    ifnull(t2.date,t3.date) as date,
    ifnull(t2.validator,t3.validator) as validator,
    ifnull(stakers,0) as stakerss, ifnull(unstakers*(-1),0) as unstakerss,stakerss+unstakerss as net_stakers
    from t2
    join t3 on t2.date=t3.date and t2.validator=t3.validator where t2.validator not like '%lockup%' and t2.date>=current_date-INTERVAL '3 MONTHS'
    and t2.validator='allnodes.poolv1.near'
    """

elif selected_option == 'Epic':
    sql2 = f"""
    with 
      t1 as (
      SELECT 
        x.block_timestamp as week,
        method_name,
        tx_signer,
        tx_receiver
      FROM near.core.fact_actions_events_function_call x
      JOIN near.core.fact_transactions y ON x.tx_hash = y.tx_hash
      WHERE method_name IN ('deposit_and_stake','unstake_all')
    ),
    t2 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as stakers
      from t1 where method_name='deposit_and_stake'
      group by 1,2
      ),
    t3 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as unstakers
      from t1 where method_name='unstake_all'
      group by 1,2
      )
    SELECT
    ifnull(t2.date,t3.date) as date,
    ifnull(t2.validator,t3.validator) as validator,
    ifnull(stakers,0) as stakerss, ifnull(unstakers*(-1),0) as unstakerss,stakerss+unstakerss as net_stakers
    from t2
    join t3 on t2.date=t3.date and t2.validator=t3.validator where t2.validator not like '%lockup%' and t2.date>=current_date-INTERVAL '3 MONTHS'
    and t2.validator='epic.poolv1.near'
    """

elif selected_option == 'Stader-labs':
    sql2 = f"""
    with 
      t1 as (
      SELECT 
        x.block_timestamp as week,
        method_name,
        tx_signer,
        tx_receiver
      FROM near.core.fact_actions_events_function_call x
      JOIN near.core.fact_transactions y ON x.tx_hash = y.tx_hash
      WHERE method_name IN ('deposit_and_stake','unstake_all')
    ),
    t2 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as stakers
      from t1 where method_name='deposit_and_stake'
      group by 1,2
      ),
    t3 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as unstakers
      from t1 where method_name='unstake_all'
      group by 1,2
      )
    SELECT
    ifnull(t2.date,t3.date) as date,
    ifnull(t2.validator,t3.validator) as validator,
    ifnull(stakers,0) as stakerss, ifnull(unstakers*(-1),0) as unstakerss,stakerss+unstakerss as net_stakers
    from t2
    join t3 on t2.date=t3.date and t2.validator=t3.validator where t2.validator not like '%lockup%' and t2.date>=current_date-INTERVAL '3 MONTHS'
    and t2.validator='v2-nearx.stader-labs.near'
    """

elif selected_option == 'Stakin':
    sql2 = f"""
    with 
      t1 as (
      SELECT 
        x.block_timestamp as week,
        method_name,
        tx_signer,
        tx_receiver
      FROM near.core.fact_actions_events_function_call x
      JOIN near.core.fact_transactions y ON x.tx_hash = y.tx_hash
      WHERE method_name IN ('deposit_and_stake','unstake_all')
    ),
    t2 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as stakers
      from t1 where method_name='deposit_and_stake'
      group by 1,2
      ),
    t3 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as unstakers
      from t1 where method_name='unstake_all'
      group by 1,2
      )
    SELECT
    ifnull(t2.date,t3.date) as date,
    ifnull(t2.validator,t3.validator) as validator,
    ifnull(stakers,0) as stakerss, ifnull(unstakers*(-1),0) as unstakerss,stakerss+unstakerss as net_stakers
    from t2
    join t3 on t2.date=t3.date and t2.validator=t3.validator where t2.validator not like '%lockup%' and t2.date>=current_date-INTERVAL '3 MONTHS'
    and t2.validator='stakin.poolv1.near'
    """

elif selected_option == 'Atomic-nodes':
    sql2 = f"""
    with 
      t1 as (
      SELECT 
        x.block_timestamp as week,
        method_name,
        tx_signer,
        tx_receiver
      FROM near.core.fact_actions_events_function_call x
      JOIN near.core.fact_transactions y ON x.tx_hash = y.tx_hash
      WHERE method_name IN ('deposit_and_stake','unstake_all')
    ),
    t2 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as stakers
      from t1 where method_name='deposit_and_stake'
      group by 1,2
      ),
    t3 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as unstakers
      from t1 where method_name='unstake_all'
      group by 1,2
      )
    SELECT
    ifnull(t2.date,t3.date) as date,
    ifnull(t2.validator,t3.validator) as validator,
    ifnull(stakers,0) as stakerss, ifnull(unstakers*(-1),0) as unstakerss,stakerss+unstakerss as net_stakers
    from t2
    join t3 on t2.date=t3.date and t2.validator=t3.validator where t2.validator not like '%lockup%' and t2.date>=current_date-INTERVAL '3 MONTHS'
    and t2.validator='atomic-nodes.poolv1.near'
    """

elif selected_option == 'Consensus Finoa 00':
    sql2 = f"""
    with 
      t1 as (
      SELECT 
        x.block_timestamp as week,
        method_name,
        tx_signer,
        tx_receiver
      FROM near.core.fact_actions_events_function_call x
      JOIN near.core.fact_transactions y ON x.tx_hash = y.tx_hash
      WHERE method_name IN ('deposit_and_stake','unstake_all')
    ),
    t2 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as stakers
      from t1 where method_name='deposit_and_stake'
      group by 1,2
      ),
    t3 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as unstakers
      from t1 where method_name='unstake_all'
      group by 1,2
      )
    SELECT
    ifnull(t2.date,t3.date) as date,
    ifnull(t2.validator,t3.validator) as validator,
    ifnull(stakers,0) as stakerss, ifnull(unstakers*(-1),0) as unstakerss,stakerss+unstakerss as net_stakers
    from t2
    join t3 on t2.date=t3.date and t2.validator=t3.validator where t2.validator not like '%lockup%' and t2.date>=current_date-INTERVAL '3 MONTHS'
    and t2.validator='consensus_finoa_00.poolv1.near'
    """

elif selected_option == 'Staked':
    sql2 = f"""
    with 
      t1 as (
      SELECT 
        x.block_timestamp as week,
        method_name,
        tx_signer,
        tx_receiver
      FROM near.core.fact_actions_events_function_call x
      JOIN near.core.fact_transactions y ON x.tx_hash = y.tx_hash
      WHERE method_name IN ('deposit_and_stake','unstake_all')
    ),
    t2 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as stakers
      from t1 where method_name='deposit_and_stake'
      group by 1,2
      ),
    t3 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as unstakers
      from t1 where method_name='unstake_all'
      group by 1,2
      )
    SELECT
    ifnull(t2.date,t3.date) as date,
    ifnull(t2.validator,t3.validator) as validator,
    ifnull(stakers,0) as stakerss, ifnull(unstakers*(-1),0) as unstakerss,stakerss+unstakerss as net_stakers
    from t2
    join t3 on t2.date=t3.date and t2.validator=t3.validator where t2.validator not like '%lockup%' and t2.date>=current_date-INTERVAL '3 MONTHS'
    and t2.validator='staked.poolv1.near'
    """

elif selected_option == 'Consensus Finoa 01':
    sql2 = f"""
    with 
      t1 as (
      SELECT 
        x.block_timestamp as week,
        method_name,
        tx_signer,
        tx_receiver
      FROM near.core.fact_actions_events_function_call x
      JOIN near.core.fact_transactions y ON x.tx_hash = y.tx_hash
      WHERE method_name IN ('deposit_and_stake','unstake_all')
    ),
    t2 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as stakers
      from t1 where method_name='deposit_and_stake'
      group by 1,2
      ),
    t3 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as unstakers
      from t1 where method_name='unstake_all'
      group by 1,2
      )
    SELECT
    ifnull(t2.date,t3.date) as date,
    ifnull(t2.validator,t3.validator) as validator,
    ifnull(stakers,0) as stakerss, ifnull(unstakers*(-1),0) as unstakerss,stakerss+unstakerss as net_stakers
    from t2
    join t3 on t2.date=t3.date and t2.validator=t3.validator where t2.validator not like '%lockup%' and t2.date>=current_date-INTERVAL '3 MONTHS'
    and t2.validator='consensus_finoa_01.poolv1.near'
    """

elif selected_option == 'Openshards':
    sql2 = f"""
    with 
      t1 as (
      SELECT 
        x.block_timestamp as week,
        method_name,
        tx_signer,
        tx_receiver
      FROM near.core.fact_actions_events_function_call x
      JOIN near.core.fact_transactions y ON x.tx_hash = y.tx_hash
      WHERE method_name IN ('deposit_and_stake','unstake_all')
    ),
    t2 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as stakers
      from t1 where method_name='deposit_and_stake'
      group by 1,2
      ),
    t3 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as unstakers
      from t1 where method_name='unstake_all'
      group by 1,2
      )
    SELECT
    ifnull(t2.date,t3.date) as date,
    ifnull(t2.validator,t3.validator) as validator,
    ifnull(stakers,0) as stakerss, ifnull(unstakers*(-1),0) as unstakerss,stakerss+unstakerss as net_stakers
    from t2
    join t3 on t2.date=t3.date and t2.validator=t3.validator where t2.validator not like '%lockup%' and t2.date>=current_date-INTERVAL '3 MONTHS'
    and t2.validator='openshards.poolv1.near'
    """

elif selected_option == 'Everstake':
    sql2 = f"""
    with 
      t1 as (
      SELECT 
        x.block_timestamp as week,
        method_name,
        tx_signer,
        tx_receiver
      FROM near.core.fact_actions_events_function_call x
      JOIN near.core.fact_transactions y ON x.tx_hash = y.tx_hash
      WHERE method_name IN ('deposit_and_stake','unstake_all')
    ),
    t2 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as stakers
      from t1 where method_name='deposit_and_stake'
      group by 1,2
      ),
    t3 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as unstakers
      from t1 where method_name='unstake_all'
      group by 1,2
      )
    SELECT
    ifnull(t2.date,t3.date) as date,
    ifnull(t2.validator,t3.validator) as validator,
    ifnull(stakers,0) as stakerss, ifnull(unstakers*(-1),0) as unstakerss,stakerss+unstakerss as net_stakers
    from t2
    join t3 on t2.date=t3.date and t2.validator=t3.validator where t2.validator not like '%lockup%' and t2.date>=current_date-INTERVAL '3 MONTHS'
    and t2.validator='everstake.poolv1.near'
    """

else:
    sql2 = f"""
    with 
      t1 as (
      SELECT 
        x.block_timestamp as week,
        method_name,
        tx_signer,
        tx_receiver
      FROM near.core.fact_actions_events_function_call x
      JOIN near.core.fact_transactions y ON x.tx_hash = y.tx_hash
      WHERE method_name IN ('deposit_and_stake','unstake_all')
    ),
    t2 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as stakers
      from t1 where method_name='deposit_and_stake'
      group by 1,2
      ),
    t3 as (
      SELECT 
        trunc(week,'week') as date,
      tx_receiver as validator,
      count(distinct tx_signer) as unstakers
      from t1 where method_name='unstake_all'
      group by 1,2
      )
    SELECT
    ifnull(t2.date,t3.date) as date,
    ifnull(t2.validator,t3.validator) as validator,
    ifnull(stakers,0) as stakerss, ifnull(unstakers*(-1),0) as unstakerss,stakerss+unstakerss as net_stakers
    from t2
    join t3 on t2.date=t3.date and t2.validator=t3.validator where t2.validator not like '%lockup%' and t2.date>=current_date-INTERVAL '3 MONTHS'
    """

# In[12]:

results2 = compute(sql2)
df2 = pd.DataFrame(results2.records)
df2.info()

st.write('')
st.write('')
base2=alt.Chart(df2).encode(x=alt.X('date:O'))
line1=base2.mark_line(color='blue').encode(y=alt.Y('sum(stakerss):Q'))
line2=base2.mark_line(color='orange').encode(y='sum(unstakerss):Q')
st.altair_chart((line1 + line2).properties(title='Weekly stakers vs unstakers over the past months',width=1200))


# In[24]:


st.altair_chart(alt.Chart(df2, height=500, width=1200)
    .mark_bar(color='green')
    .encode(x='date:O', y='sum(net_stakers):Q')
    .properties(title='Weekly net stakers over the past months'))


# In[16]:


st.altair_chart(alt.Chart(df2, height=500, width=1200)
    .mark_bar()
    .encode(x='date:O', y='net_stakers:Q',color=alt.Color('validator', scale=alt.Scale(scheme='dark2')))
    .properties(title='Weekly net_stakers by chosen validator'))
         
         

         
if selected_option == 'Binancenode1':
    sql2 = f"""
    WITH 
       transactions as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name IN ('deposit_and_stake') and block_timestamp>=current_date-INTERVAL'3 MONTHS'
       ),
       stakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
    FROM near.core.fact_transactions
      WHERE tx_hash in (select * from transactions)
    ),
       transactions2 as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name ='unstake_all'
       ),
       unstakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:receipt[0]:outcome:logs[0] as col,
      substring(col, CHARINDEX('Withdraw', col) + 8, CHARINDEX('NEAR', col) - CHARINDEX('Withdraw', col) - 8) as final, case when final <> '' then final/pow(10,18) else 0 end as near_unstaked FROM near.core.fact_transactions where tx:receipt[0]:outcome:logs[0] like 'Withdraw%'
      and tx_hash in (select * from transactions2)
    ),
    weekly as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_staked
       --amount_staked/pow(10,24) as near_staked
    FROM stakes x
       WHERE near_staked is not null 
    ),
       weekly2 as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_unstaked
       --amount_staked/pow(10,24) as near_staked
    FROM unstakes x
       WHERE near_unstaked is not null 
    ),
      totals as (
       SELECT
       x.weeks,
       sum(near_staked) as week_near_staked,
       sum(week_near_staked) over (order by x.weeks)as total_near_staked,
       sum(near_unstaked) as week_near_unstaked,
       sum(week_near_unstaked) over (order by x.weeks)as total_near_unstaked
       from weekly x
       full outer join weekly2 y on x.weeks=y.weeks
       group by 1 order by 1
       ),
       totals2 as (
       SELECT
       weeks,
       week_near_staked- week_near_unstaked as week_near_staked,
       total_near_staked-total_near_unstaked as total_near_staked
       from totals
       ),
    ranking1 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_staked) as total_near_delegated,
    sum(total_near_delegated) over (partition by validator order by weeks) as cumulative_near_delegated
    FROM weekly 
    group by 1,2
    ),
       ranking2 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_unstaked) as total_near_undelegated,
    sum(total_near_undelegated) over (partition by validator order by weeks) as cumulative_near_undelegated
    FROM weekly2 
    group by 1,2
    )
       SELECT
       ifnull(x.weeks,y.weeks) as weeks,
       ifnull(x.validator,y.validator) as validator,
       ifnull(total_near_delegated,0) as near_staked,
       ifnull(total_near_undelegated,0) as near_unstaked,
       ifnull(total_near_delegated,0)-ifnull(total_near_undelegated,0) as total_near_delegated,
       ifnull(cumulative_near_delegated,0)-ifnull(cumulative_near_undelegated,0) as cumulative_near_delegated
       from ranking1 x
       full outer join ranking2 y on x.weeks=y.weeks and x.validator=y.validator
       where x.weeks >=current_date-INTERVAL '3 MONTHS'
       and x.validator='binancenode1.poolv1.near'
    """
elif selected_option == 'Figment':
    sql2 = f"""
    WITH 
       transactions as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name IN ('deposit_and_stake')
       ),
       stakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
    FROM near.core.fact_transactions
      WHERE tx_hash in (select * from transactions)
    ),
       transactions2 as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name ='unstake_all'
       ),
       unstakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:receipt[0]:outcome:logs[0] as col,
      substring(col, CHARINDEX('Withdraw', col) + 8, CHARINDEX('NEAR', col) - CHARINDEX('Withdraw', col) - 8) as final, case when final <> '' then final/pow(10,18) else 0 end as near_unstaked
    FROM near.core.fact_transactions where tx:receipt[0]:outcome:logs[0] like 'Withdraw%'
      and tx_hash in (select * from transactions2)
    ),
    weekly as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_staked
       --amount_staked/pow(10,24) as near_staked
    FROM stakes x
       WHERE near_staked is not null 
    ),
       weekly2 as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_unstaked
       --amount_staked/pow(10,24) as near_staked
    FROM unstakes x
       WHERE near_unstaked is not null 
    ),
      totals as (
       SELECT
       x.weeks,
       sum(near_staked) as week_near_staked,
       sum(week_near_staked) over (order by x.weeks)as total_near_staked,
       sum(near_unstaked) as week_near_unstaked,
       sum(week_near_unstaked) over (order by x.weeks)as total_near_unstaked
       from weekly x
       full outer join weekly2 y on x.weeks=y.weeks
       group by 1 order by 1
       ),
       totals2 as (
       SELECT
       weeks,
       week_near_staked- week_near_unstaked as week_near_staked,
       total_near_staked-total_near_unstaked as total_near_staked
       from totals
       ),
    ranking1 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_staked) as total_near_delegated,
    sum(total_near_delegated) over (partition by validator order by weeks) as cumulative_near_delegated
    FROM weekly 
    group by 1,2
    ),
       ranking2 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_unstaked) as total_near_undelegated,
    sum(total_near_undelegated) over (partition by validator order by weeks) as cumulative_near_undelegated
    FROM weekly2 
    group by 1,2
    )
       SELECT
       ifnull(x.weeks,y.weeks) as weeks,
       ifnull(x.validator,y.validator) as validator,
       ifnull(total_near_delegated,0) as near_staked,
       ifnull(total_near_undelegated,0) as near_unstaked,
       ifnull(total_near_delegated,0)-ifnull(total_near_undelegated,0) as total_near_delegated,
       ifnull(cumulative_near_delegated,0)-ifnull(cumulative_near_undelegated,0) as cumulative_near_delegated
       from ranking1 x
       full outer join ranking2 y on x.weeks=y.weeks and x.validator=y.validator
       where x.weeks >=current_date-INTERVAL '3 MONTHS'
        and x.validator='figment.poolv1.near'
    """
elif selected_option == 'Astro-Stakers':
    sql2 = f"""
    WITH 
       transactions as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name IN ('deposit_and_stake')
       ),
       stakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
    FROM near.core.fact_transactions
      WHERE tx_hash in (select * from transactions)
    ),
       transactions2 as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name ='unstake_all'
       ),
       unstakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:receipt[0]:outcome:logs[0] as col,
      substring(col, CHARINDEX('Withdraw', col) + 8, CHARINDEX('NEAR', col) - CHARINDEX('Withdraw', col) - 8) as final, case when final <> '' then final/pow(10,18) else 0 end as near_unstaked
    FROM near.core.fact_transactions where tx:receipt[0]:outcome:logs[0] like 'Withdraw%'
      and tx_hash in (select * from transactions2)
    ),
    weekly as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_staked
       --amount_staked/pow(10,24) as near_staked
    FROM stakes x
       WHERE near_staked is not null 
    ),
       weekly2 as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_unstaked
       --amount_staked/pow(10,24) as near_staked
    FROM unstakes x
       WHERE near_unstaked is not null 
    ),
      totals as (
       SELECT
       x.weeks,
       sum(near_staked) as week_near_staked,
       sum(week_near_staked) over (order by x.weeks)as total_near_staked,
       sum(near_unstaked) as week_near_unstaked,
       sum(week_near_unstaked) over (order by x.weeks)as total_near_unstaked
       from weekly x
       full outer join weekly2 y on x.weeks=y.weeks
       group by 1 order by 1
       ),
       totals2 as (
       SELECT
       weeks,
       week_near_staked- week_near_unstaked as week_near_staked,
       total_near_staked-total_near_unstaked as total_near_staked
       from totals
       ),
    ranking1 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_staked) as total_near_delegated,
    sum(total_near_delegated) over (partition by validator order by weeks) as cumulative_near_delegated
    FROM weekly 
    group by 1,2
    ),
       ranking2 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_unstaked) as total_near_undelegated,
    sum(total_near_undelegated) over (partition by validator order by weeks) as cumulative_near_undelegated
    FROM weekly2 
    group by 1,2
    )
       SELECT
       ifnull(x.weeks,y.weeks) as weeks,
       ifnull(x.validator,y.validator) as validator,
       ifnull(total_near_delegated,0) as near_staked,
       ifnull(total_near_undelegated,0) as near_unstaked,
       ifnull(total_near_delegated,0)-ifnull(total_near_undelegated,0) as total_near_delegated,
       ifnull(cumulative_near_delegated,0)-ifnull(cumulative_near_undelegated,0) as cumulative_near_delegated
       from ranking1 x
       full outer join ranking2 y on x.weeks=y.weeks and x.validator=y.validator
       where x.weeks >=current_date-INTERVAL '3 MONTHS'
    and x.validator='astro-stakers.poolv1.near'
    """
         
elif selected_option == 'Near-Fans':
    sql2 = f"""
    WITH 
       transactions as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name IN ('deposit_and_stake')
       ),
       stakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
    FROM near.core.fact_transactions
      WHERE tx_hash in (select * from transactions)
    ),
       transactions2 as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name ='unstake_all'
       ),
       unstakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:receipt[0]:outcome:logs[0] as col,
      substring(col, CHARINDEX('Withdraw', col) + 8, CHARINDEX('NEAR', col) - CHARINDEX('Withdraw', col) - 8) as final, case when final <> '' then final/pow(10,18) else 0 end as near_unstaked
    FROM near.core.fact_transactions where tx:receipt[0]:outcome:logs[0] like 'Withdraw%'
      and tx_hash in (select * from transactions2)
    ),
    weekly as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_staked
       --amount_staked/pow(10,24) as near_staked
    FROM stakes x
       WHERE near_staked is not null 
    ),
       weekly2 as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_unstaked
       --amount_staked/pow(10,24) as near_staked
    FROM unstakes x
       WHERE near_unstaked is not null 
    ),
      totals as (
       SELECT
       x.weeks,
       sum(near_staked) as week_near_staked,
       sum(week_near_staked) over (order by x.weeks)as total_near_staked,
       sum(near_unstaked) as week_near_unstaked,
       sum(week_near_unstaked) over (order by x.weeks)as total_near_unstaked
       from weekly x
       full outer join weekly2 y on x.weeks=y.weeks
       group by 1 order by 1
       ),
       totals2 as (
       SELECT
       weeks,
       week_near_staked- week_near_unstaked as week_near_staked,
       total_near_staked-total_near_unstaked as total_near_staked
       from totals
       ),
    ranking1 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_staked) as total_near_delegated,
    sum(total_near_delegated) over (partition by validator order by weeks) as cumulative_near_delegated
    FROM weekly 
    group by 1,2
    ),
       ranking2 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_unstaked) as total_near_undelegated,
    sum(total_near_undelegated) over (partition by validator order by weeks) as cumulative_near_undelegated
    FROM weekly2 
    group by 1,2
    )
       SELECT
       ifnull(x.weeks,y.weeks) as weeks,
       ifnull(x.validator,y.validator) as validator,
       ifnull(total_near_delegated,0) as near_staked,
       ifnull(total_near_undelegated,0) as near_unstaked,
       ifnull(total_near_delegated,0)-ifnull(total_near_undelegated,0) as total_near_delegated,
       ifnull(cumulative_near_delegated,0)-ifnull(cumulative_near_undelegated,0) as cumulative_near_delegated
       from ranking1 x
       full outer join ranking2 y on x.weeks=y.weeks and x.validator=y.validator
       where x.weeks >=current_date-INTERVAL '3 MONTHS'
    and x.validator='near-fans.poolv1.near'
    """

elif selected_option == 'Blockdaemon':
    sql2 = f"""
    WITH 
       transactions as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name IN ('deposit_and_stake')
       ),
       stakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
    FROM near.core.fact_transactions
      WHERE tx_hash in (select * from transactions)
    ),
       transactions2 as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name ='unstake_all'
       ),
       unstakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:receipt[0]:outcome:logs[0] as col,
      substring(col, CHARINDEX('Withdraw', col) + 8, CHARINDEX('NEAR', col) - CHARINDEX('Withdraw', col) - 8) as final, case when final <> '' then final/pow(10,18) else 0 end as near_unstaked
    FROM near.core.fact_transactions where tx:receipt[0]:outcome:logs[0] like 'Withdraw%'
      and tx_hash in (select * from transactions2)
    ),
    weekly as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_staked
       --amount_staked/pow(10,24) as near_staked
    FROM stakes x
       WHERE near_staked is not null 
    ),
       weekly2 as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_unstaked
       --amount_staked/pow(10,24) as near_staked
    FROM unstakes x
       WHERE near_unstaked is not null 
    ),
      totals as (
       SELECT
       x.weeks,
       sum(near_staked) as week_near_staked,
       sum(week_near_staked) over (order by x.weeks)as total_near_staked,
       sum(near_unstaked) as week_near_unstaked,
       sum(week_near_unstaked) over (order by x.weeks)as total_near_unstaked
       from weekly x
       full outer join weekly2 y on x.weeks=y.weeks
       group by 1 order by 1
       ),
       totals2 as (
       SELECT
       weeks,
       week_near_staked- week_near_unstaked as week_near_staked,
       total_near_staked-total_near_unstaked as total_near_staked
       from totals
       ),
    ranking1 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_staked) as total_near_delegated,
    sum(total_near_delegated) over (partition by validator order by weeks) as cumulative_near_delegated
    FROM weekly 
    group by 1,2
    ),
       ranking2 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_unstaked) as total_near_undelegated,
    sum(total_near_undelegated) over (partition by validator order by weeks) as cumulative_near_undelegated
    FROM weekly2 
    group by 1,2
    )
       SELECT
       ifnull(x.weeks,y.weeks) as weeks,
       ifnull(x.validator,y.validator) as validator,
       ifnull(total_near_delegated,0) as near_staked,
       ifnull(total_near_undelegated,0) as near_unstaked,
       ifnull(total_near_delegated,0)-ifnull(total_near_undelegated,0) as total_near_delegated,
       ifnull(cumulative_near_delegated,0)-ifnull(cumulative_near_undelegated,0) as cumulative_near_delegated
       from ranking1 x
       full outer join ranking2 y on x.weeks=y.weeks and x.validator=y.validator
       where x.weeks >=current_date-INTERVAL '3 MONTHS'
    and x.validator='blockdaemon.poolv1.near'
    """
         
elif selected_option == 'Stake1':
    sql2 = f"""
    WITH 
       transactions as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name IN ('deposit_and_stake')
       ),
       stakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
    FROM near.core.fact_transactions
      WHERE tx_hash in (select * from transactions)
    ),
       transactions2 as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name ='unstake_all'
       ),
       unstakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:receipt[0]:outcome:logs[0] as col,
      substring(col, CHARINDEX('Withdraw', col) + 8, CHARINDEX('NEAR', col) - CHARINDEX('Withdraw', col) - 8) as final, case when final <> '' then final/pow(10,18) else 0 end as near_unstaked
    FROM near.core.fact_transactions where tx:receipt[0]:outcome:logs[0] like 'Withdraw%'
      and tx_hash in (select * from transactions2)
    ),
    weekly as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_staked
       --amount_staked/pow(10,24) as near_staked
    FROM stakes x
       WHERE near_staked is not null 
    ),
       weekly2 as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_unstaked
       --amount_staked/pow(10,24) as near_staked
    FROM unstakes x
       WHERE near_unstaked is not null 
    ),
      totals as (
       SELECT
       x.weeks,
       sum(near_staked) as week_near_staked,
       sum(week_near_staked) over (order by x.weeks)as total_near_staked,
       sum(near_unstaked) as week_near_unstaked,
       sum(week_near_unstaked) over (order by x.weeks)as total_near_unstaked
       from weekly x
       full outer join weekly2 y on x.weeks=y.weeks
       group by 1 order by 1
       ),
       totals2 as (
       SELECT
       weeks,
       week_near_staked- week_near_unstaked as week_near_staked,
       total_near_staked-total_near_unstaked as total_near_staked
       from totals
       ),
    ranking1 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_staked) as total_near_delegated,
    sum(total_near_delegated) over (partition by validator order by weeks) as cumulative_near_delegated
    FROM weekly 
    group by 1,2
    ),
       ranking2 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_unstaked) as total_near_undelegated,
    sum(total_near_undelegated) over (partition by validator order by weeks) as cumulative_near_undelegated
    FROM weekly2 
    group by 1,2
    )
       SELECT
       ifnull(x.weeks,y.weeks) as weeks,
       ifnull(x.validator,y.validator) as validator,
       ifnull(total_near_delegated,0) as near_staked,
       ifnull(total_near_undelegated,0) as near_unstaked,
       ifnull(total_near_delegated,0)-ifnull(total_near_undelegated,0) as total_near_delegated,
       ifnull(cumulative_near_delegated,0)-ifnull(cumulative_near_undelegated,0) as cumulative_near_delegated
       from ranking1 x
       full outer join ranking2 y on x.weeks=y.weeks and x.validator=y.validator
       where x.weeks >=current_date-INTERVAL '3 MONTHS'
    and x.validator='stake1.poolv1.near'
    """
         
elif selected_option == 'Zavodil':
    sql2 = f"""
    WITH 
       transactions as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name IN ('deposit_and_stake')
       ),
       stakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
    FROM near.core.fact_transactions
      WHERE tx_hash in (select * from transactions)
    ),
       transactions2 as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name ='unstake_all'
       ),
       unstakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:receipt[0]:outcome:logs[0] as col,
      substring(col, CHARINDEX('Withdraw', col) + 8, CHARINDEX('NEAR', col) - CHARINDEX('Withdraw', col) - 8) as final, case when final <> '' then final/pow(10,18) else 0 end as near_unstaked
    FROM near.core.fact_transactions where tx:receipt[0]:outcome:logs[0] like 'Withdraw%'
      and tx_hash in (select * from transactions2)
    ),
    weekly as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_staked
       --amount_staked/pow(10,24) as near_staked
    FROM stakes x
       WHERE near_staked is not null 
    ),
       weekly2 as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_unstaked
       --amount_staked/pow(10,24) as near_staked
    FROM unstakes x
       WHERE near_unstaked is not null 
    ),
      totals as (
       SELECT
       x.weeks,
       sum(near_staked) as week_near_staked,
       sum(week_near_staked) over (order by x.weeks)as total_near_staked,
       sum(near_unstaked) as week_near_unstaked,
       sum(week_near_unstaked) over (order by x.weeks)as total_near_unstaked
       from weekly x
       full outer join weekly2 y on x.weeks=y.weeks
       group by 1 order by 1
       ),
       totals2 as (
       SELECT
       weeks,
       week_near_staked- week_near_unstaked as week_near_staked,
       total_near_staked-total_near_unstaked as total_near_staked
       from totals
       ),
    ranking1 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_staked) as total_near_delegated,
    sum(total_near_delegated) over (partition by validator order by weeks) as cumulative_near_delegated
    FROM weekly 
    group by 1,2
    ),
       ranking2 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_unstaked) as total_near_undelegated,
    sum(total_near_undelegated) over (partition by validator order by weeks) as cumulative_near_undelegated
    FROM weekly2 
    group by 1,2
    )
       SELECT
       ifnull(x.weeks,y.weeks) as weeks,
       ifnull(x.validator,y.validator) as validator,
       ifnull(total_near_delegated,0) as near_staked,
       ifnull(total_near_undelegated,0) as near_unstaked,
       ifnull(total_near_delegated,0)-ifnull(total_near_undelegated,0) as total_near_delegated,
       ifnull(cumulative_near_delegated,0)-ifnull(cumulative_near_undelegated,0) as cumulative_near_delegated
       from ranking1 x
       full outer join ranking2 y on x.weeks=y.weeks and x.validator=y.validator
       where x.weeks >=current_date-INTERVAL '3 MONTHS'
    and x.validator='zavodil.poolv1.near'
    """
         
elif selected_option == 'Legends':
    sql2 = f"""
    WITH 
       transactions as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name IN ('deposit_and_stake')
       ),
       stakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
    FROM near.core.fact_transactions
      WHERE tx_hash in (select * from transactions)
    ),
       transactions2 as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name ='unstake_all'
       ),
       unstakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:receipt[0]:outcome:logs[0] as col,
      substring(col, CHARINDEX('Withdraw', col) + 8, CHARINDEX('NEAR', col) - CHARINDEX('Withdraw', col) - 8) as final, case when final <> '' then final/pow(10,18) else 0 end as near_unstaked
    FROM near.core.fact_transactions where tx:receipt[0]:outcome:logs[0] like 'Withdraw%'
      and tx_hash in (select * from transactions2)
    ),
    weekly as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_staked
       --amount_staked/pow(10,24) as near_staked
    FROM stakes x
       WHERE near_staked is not null 
    ),
       weekly2 as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_unstaked
       --amount_staked/pow(10,24) as near_staked
    FROM unstakes x
       WHERE near_unstaked is not null 
    ),
      totals as (
       SELECT
       x.weeks,
       sum(near_staked) as week_near_staked,
       sum(week_near_staked) over (order by x.weeks)as total_near_staked,
       sum(near_unstaked) as week_near_unstaked,
       sum(week_near_unstaked) over (order by x.weeks)as total_near_unstaked
       from weekly x
       full outer join weekly2 y on x.weeks=y.weeks
       group by 1 order by 1
       ),
       totals2 as (
       SELECT
       weeks,
       week_near_staked- week_near_unstaked as week_near_staked,
       total_near_staked-total_near_unstaked as total_near_staked
       from totals
       ),
    ranking1 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_staked) as total_near_delegated,
    sum(total_near_delegated) over (partition by validator order by weeks) as cumulative_near_delegated
    FROM weekly 
    group by 1,2
    ),
       ranking2 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_unstaked) as total_near_undelegated,
    sum(total_near_undelegated) over (partition by validator order by weeks) as cumulative_near_undelegated
    FROM weekly2 
    group by 1,2
    )
       SELECT
       ifnull(x.weeks,y.weeks) as weeks,
       ifnull(x.validator,y.validator) as validator,
       ifnull(total_near_delegated,0) as near_staked,
       ifnull(total_near_undelegated,0) as near_unstaked,
       ifnull(total_near_delegated,0)-ifnull(total_near_undelegated,0) as total_near_delegated,
       ifnull(cumulative_near_delegated,0)-ifnull(cumulative_near_undelegated,0) as cumulative_near_delegated
       from ranking1 x
       full outer join ranking2 y on x.weeks=y.weeks and x.validator=y.validator
       where x.weeks >=current_date-INTERVAL '3 MONTHS'
    and x.validator='legends.poolv1.near'
    """
         
elif selected_option == 'Meta-pool':
    sql2 = f"""
    WITH 
       transactions as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name IN ('deposit_and_stake')
       ),
       stakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
    FROM near.core.fact_transactions
      WHERE tx_hash in (select * from transactions)
    ),
       transactions2 as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name ='unstake_all'
       ),
       unstakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:receipt[0]:outcome:logs[0] as col,
      substring(col, CHARINDEX('Withdraw', col) + 8, CHARINDEX('NEAR', col) - CHARINDEX('Withdraw', col) - 8) as final, case when final <> '' then final/pow(10,18) else 0 end as near_unstaked
    FROM near.core.fact_transactions where tx:receipt[0]:outcome:logs[0] like 'Withdraw%'
      and tx_hash in (select * from transactions2)
    ),
    weekly as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_staked
       --amount_staked/pow(10,24) as near_staked
    FROM stakes x
       WHERE near_staked is not null 
    ),
       weekly2 as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_unstaked
       --amount_staked/pow(10,24) as near_staked
    FROM unstakes x
       WHERE near_unstaked is not null 
    ),
      totals as (
       SELECT
       x.weeks,
       sum(near_staked) as week_near_staked,
       sum(week_near_staked) over (order by x.weeks)as total_near_staked,
       sum(near_unstaked) as week_near_unstaked,
       sum(week_near_unstaked) over (order by x.weeks)as total_near_unstaked
       from weekly x
       full outer join weekly2 y on x.weeks=y.weeks
       group by 1 order by 1
       ),
       totals2 as (
       SELECT
       weeks,
       week_near_staked- week_near_unstaked as week_near_staked,
       total_near_staked-total_near_unstaked as total_near_staked
       from totals
       ),
    ranking1 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_staked) as total_near_delegated,
    sum(total_near_delegated) over (partition by validator order by weeks) as cumulative_near_delegated
    FROM weekly 
    group by 1,2
    ),
       ranking2 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_unstaked) as total_near_undelegated,
    sum(total_near_undelegated) over (partition by validator order by weeks) as cumulative_near_undelegated
    FROM weekly2 
    group by 1,2
    )
       SELECT
       ifnull(x.weeks,y.weeks) as weeks,
       ifnull(x.validator,y.validator) as validator,
       ifnull(total_near_delegated,0) as near_staked,
       ifnull(total_near_undelegated,0) as near_unstaked,
       ifnull(total_near_delegated,0)-ifnull(total_near_undelegated,0) as total_near_delegated,
       ifnull(cumulative_near_delegated,0)-ifnull(cumulative_near_undelegated,0) as cumulative_near_delegated
       from ranking1 x
       full outer join ranking2 y on x.weeks=y.weeks and x.validator=y.validator
       where x.weeks >=current_date-INTERVAL '3 MONTHS'
    and x.validator='meta-pool.near'
    """

elif selected_option == 'Hashquark':
    sql2 = f"""
    WITH 
       transactions as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name IN ('deposit_and_stake')
       ),
       stakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
    FROM near.core.fact_transactions
      WHERE tx_hash in (select * from transactions)
    ),
       transactions2 as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name ='unstake_all'
       ),
       unstakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:receipt[0]:outcome:logs[0] as col,
      substring(col, CHARINDEX('Withdraw', col) + 8, CHARINDEX('NEAR', col) - CHARINDEX('Withdraw', col) - 8) as final, case when final <> '' then final/pow(10,18) else 0 end as near_unstaked
    FROM near.core.fact_transactions where tx:receipt[0]:outcome:logs[0] like 'Withdraw%'
      and tx_hash in (select * from transactions2)
    ),
    weekly as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_staked
       --amount_staked/pow(10,24) as near_staked
    FROM stakes x
       WHERE near_staked is not null 
    ),
       weekly2 as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_unstaked
       --amount_staked/pow(10,24) as near_staked
    FROM unstakes x
       WHERE near_unstaked is not null 
    ),
      totals as (
       SELECT
       x.weeks,
       sum(near_staked) as week_near_staked,
       sum(week_near_staked) over (order by x.weeks)as total_near_staked,
       sum(near_unstaked) as week_near_unstaked,
       sum(week_near_unstaked) over (order by x.weeks)as total_near_unstaked
       from weekly x
       full outer join weekly2 y on x.weeks=y.weeks
       group by 1 order by 1
       ),
       totals2 as (
       SELECT
       weeks,
       week_near_staked- week_near_unstaked as week_near_staked,
       total_near_staked-total_near_unstaked as total_near_staked
       from totals
       ),
    ranking1 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_staked) as total_near_delegated,
    sum(total_near_delegated) over (partition by validator order by weeks) as cumulative_near_delegated
    FROM weekly 
    group by 1,2
    ),
       ranking2 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_unstaked) as total_near_undelegated,
    sum(total_near_undelegated) over (partition by validator order by weeks) as cumulative_near_undelegated
    FROM weekly2 
    group by 1,2
    )
       SELECT
       ifnull(x.weeks,y.weeks) as weeks,
       ifnull(x.validator,y.validator) as validator,
       ifnull(total_near_delegated,0) as near_staked,
       ifnull(total_near_undelegated,0) as near_unstaked,
       ifnull(total_near_delegated,0)-ifnull(total_near_undelegated,0) as total_near_delegated,
       ifnull(cumulative_near_delegated,0)-ifnull(cumulative_near_undelegated,0) as cumulative_near_delegated
       from ranking1 x
       full outer join ranking2 y on x.weeks=y.weeks and x.validator=y.validator
       where x.weeks >=current_date-INTERVAL '3 MONTHS'
    and x.validator='hashquark.poolv1.near'
    """

elif selected_option == 'Allnodes':
    sql2 = f"""
    WITH 
       transactions as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name IN ('deposit_and_stake')
       ),
       stakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
    FROM near.core.fact_transactions
      WHERE tx_hash in (select * from transactions)
    ),
       transactions2 as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name ='unstake_all'
       ),
       unstakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:receipt[0]:outcome:logs[0] as col,
      substring(col, CHARINDEX('Withdraw', col) + 8, CHARINDEX('NEAR', col) - CHARINDEX('Withdraw', col) - 8) as final, case when final <> '' then final/pow(10,18) else 0 end as near_unstaked
    FROM near.core.fact_transactions where tx:receipt[0]:outcome:logs[0] like 'Withdraw%'
      and tx_hash in (select * from transactions2)
    ),
    weekly as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_staked
       --amount_staked/pow(10,24) as near_staked
    FROM stakes x
       WHERE near_staked is not null 
    ),
       weekly2 as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_unstaked
       --amount_staked/pow(10,24) as near_staked
    FROM unstakes x
       WHERE near_unstaked is not null 
    ),
      totals as (
       SELECT
       x.weeks,
       sum(near_staked) as week_near_staked,
       sum(week_near_staked) over (order by x.weeks)as total_near_staked,
       sum(near_unstaked) as week_near_unstaked,
       sum(week_near_unstaked) over (order by x.weeks)as total_near_unstaked
       from weekly x
       full outer join weekly2 y on x.weeks=y.weeks
       group by 1 order by 1
       ),
       totals2 as (
       SELECT
       weeks,
       week_near_staked- week_near_unstaked as week_near_staked,
       total_near_staked-total_near_unstaked as total_near_staked
       from totals
       ),
    ranking1 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_staked) as total_near_delegated,
    sum(total_near_delegated) over (partition by validator order by weeks) as cumulative_near_delegated
    FROM weekly 
    group by 1,2
    ),
       ranking2 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_unstaked) as total_near_undelegated,
    sum(total_near_undelegated) over (partition by validator order by weeks) as cumulative_near_undelegated
    FROM weekly2 
    group by 1,2
    )
       SELECT
       ifnull(x.weeks,y.weeks) as weeks,
       ifnull(x.validator,y.validator) as validator,
       ifnull(total_near_delegated,0) as near_staked,
       ifnull(total_near_undelegated,0) as near_unstaked,
       ifnull(total_near_delegated,0)-ifnull(total_near_undelegated,0) as total_near_delegated,
       ifnull(cumulative_near_delegated,0)-ifnull(cumulative_near_undelegated,0) as cumulative_near_delegated
       from ranking1 x
       full outer join ranking2 y on x.weeks=y.weeks and x.validator=y.validator
       where x.weeks >=current_date-INTERVAL '3 MONTHS'
    and x.validator='allnodes.poolv1.near'
    """

elif selected_option == 'Epic':
    sql2 = f"""
    WITH 
       transactions as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name IN ('deposit_and_stake')
       ),
       stakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
    FROM near.core.fact_transactions
      WHERE tx_hash in (select * from transactions)
    ),
       transactions2 as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name ='unstake_all'
       ),
       unstakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:receipt[0]:outcome:logs[0] as col,
      substring(col, CHARINDEX('Withdraw', col) + 8, CHARINDEX('NEAR', col) - CHARINDEX('Withdraw', col) - 8) as final, case when final <> '' then final/pow(10,18) else 0 end as near_unstaked
    FROM near.core.fact_transactions where tx:receipt[0]:outcome:logs[0] like 'Withdraw%'
      and tx_hash in (select * from transactions2)
    ),
    weekly as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_staked
       --amount_staked/pow(10,24) as near_staked
    FROM stakes x
       WHERE near_staked is not null 
    ),
       weekly2 as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_unstaked
       --amount_staked/pow(10,24) as near_staked
    FROM unstakes x
       WHERE near_unstaked is not null 
    ),
      totals as (
       SELECT
       x.weeks,
       sum(near_staked) as week_near_staked,
       sum(week_near_staked) over (order by x.weeks)as total_near_staked,
       sum(near_unstaked) as week_near_unstaked,
       sum(week_near_unstaked) over (order by x.weeks)as total_near_unstaked
       from weekly x
       full outer join weekly2 y on x.weeks=y.weeks
       group by 1 order by 1
       ),
       totals2 as (
       SELECT
       weeks,
       week_near_staked- week_near_unstaked as week_near_staked,
       total_near_staked-total_near_unstaked as total_near_staked
       from totals
       ),
    ranking1 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_staked) as total_near_delegated,
    sum(total_near_delegated) over (partition by validator order by weeks) as cumulative_near_delegated
    FROM weekly 
    group by 1,2
    ),
       ranking2 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_unstaked) as total_near_undelegated,
    sum(total_near_undelegated) over (partition by validator order by weeks) as cumulative_near_undelegated
    FROM weekly2 
    group by 1,2
    )
       SELECT
       ifnull(x.weeks,y.weeks) as weeks,
       ifnull(x.validator,y.validator) as validator,
       ifnull(total_near_delegated,0) as near_staked,
       ifnull(total_near_undelegated,0) as near_unstaked,
       ifnull(total_near_delegated,0)-ifnull(total_near_undelegated,0) as total_near_delegated,
       ifnull(cumulative_near_delegated,0)-ifnull(cumulative_near_undelegated,0) as cumulative_near_delegated
       from ranking1 x
       full outer join ranking2 y on x.weeks=y.weeks and x.validator=y.validator
       where x.weeks >=current_date-INTERVAL '3 MONTHS'
    and x.validator='epic.poolv1.near'
    """

elif selected_option == 'Stader-labs':
    sql2 = f"""
    WITH 
       transactions as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name IN ('deposit_and_stake')
       ),
       stakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
    FROM near.core.fact_transactions
      WHERE tx_hash in (select * from transactions)
    ),
       transactions2 as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name ='unstake_all'
       ),
       unstakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:receipt[0]:outcome:logs[0] as col,
      substring(col, CHARINDEX('Withdraw', col) + 8, CHARINDEX('NEAR', col) - CHARINDEX('Withdraw', col) - 8) as final, case when final <> '' then final/pow(10,18) else 0 end as near_unstaked
    FROM near.core.fact_transactions where tx:receipt[0]:outcome:logs[0] like 'Withdraw%'
      and tx_hash in (select * from transactions2)
    ),
    weekly as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_staked
       --amount_staked/pow(10,24) as near_staked
    FROM stakes x
       WHERE near_staked is not null 
    ),
       weekly2 as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_unstaked
       --amount_staked/pow(10,24) as near_staked
    FROM unstakes x
       WHERE near_unstaked is not null 
    ),
      totals as (
       SELECT
       x.weeks,
       sum(near_staked) as week_near_staked,
       sum(week_near_staked) over (order by x.weeks)as total_near_staked,
       sum(near_unstaked) as week_near_unstaked,
       sum(week_near_unstaked) over (order by x.weeks)as total_near_unstaked
       from weekly x
       full outer join weekly2 y on x.weeks=y.weeks
       group by 1 order by 1
       ),
       totals2 as (
       SELECT
       weeks,
       week_near_staked- week_near_unstaked as week_near_staked,
       total_near_staked-total_near_unstaked as total_near_staked
       from totals
       ),
    ranking1 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_staked) as total_near_delegated,
    sum(total_near_delegated) over (partition by validator order by weeks) as cumulative_near_delegated
    FROM weekly 
    group by 1,2
    ),
       ranking2 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_unstaked) as total_near_undelegated,
    sum(total_near_undelegated) over (partition by validator order by weeks) as cumulative_near_undelegated
    FROM weekly2 
    group by 1,2
    )
       SELECT
       ifnull(x.weeks,y.weeks) as weeks,
       ifnull(x.validator,y.validator) as validator,
       ifnull(total_near_delegated,0) as near_staked,
       ifnull(total_near_undelegated,0) as near_unstaked,
       ifnull(total_near_delegated,0)-ifnull(total_near_undelegated,0) as total_near_delegated,
       ifnull(cumulative_near_delegated,0)-ifnull(cumulative_near_undelegated,0) as cumulative_near_delegated
       from ranking1 x
       full outer join ranking2 y on x.weeks=y.weeks and x.validator=y.validator
       where x.weeks >=current_date-INTERVAL '3 MONTHS'
    and x.validator='v2-nearx.stader-labs.near'
    """

elif selected_option == 'Stakin':
    sql2 = f"""
    WITH 
       transactions as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name IN ('deposit_and_stake')
       ),
       stakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
    FROM near.core.fact_transactions
      WHERE tx_hash in (select * from transactions)
    ),
       transactions2 as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name ='unstake_all'
       ),
       unstakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:receipt[0]:outcome:logs[0] as col,
      substring(col, CHARINDEX('Withdraw', col) + 8, CHARINDEX('NEAR', col) - CHARINDEX('Withdraw', col) - 8) as final, case when final <> '' then final/pow(10,18) else 0 end as near_unstaked
    FROM near.core.fact_transactions where tx:receipt[0]:outcome:logs[0] like 'Withdraw%'
      and tx_hash in (select * from transactions2)
    ),
    weekly as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_staked
       --amount_staked/pow(10,24) as near_staked
    FROM stakes x
       WHERE near_staked is not null 
    ),
       weekly2 as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_unstaked
       --amount_staked/pow(10,24) as near_staked
    FROM unstakes x
       WHERE near_unstaked is not null 
    ),
      totals as (
       SELECT
       x.weeks,
       sum(near_staked) as week_near_staked,
       sum(week_near_staked) over (order by x.weeks)as total_near_staked,
       sum(near_unstaked) as week_near_unstaked,
       sum(week_near_unstaked) over (order by x.weeks)as total_near_unstaked
       from weekly x
       full outer join weekly2 y on x.weeks=y.weeks
       group by 1 order by 1
       ),
       totals2 as (
       SELECT
       weeks,
       week_near_staked- week_near_unstaked as week_near_staked,
       total_near_staked-total_near_unstaked as total_near_staked
       from totals
       ),
    ranking1 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_staked) as total_near_delegated,
    sum(total_near_delegated) over (partition by validator order by weeks) as cumulative_near_delegated
    FROM weekly 
    group by 1,2
    ),
       ranking2 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_unstaked) as total_near_undelegated,
    sum(total_near_undelegated) over (partition by validator order by weeks) as cumulative_near_undelegated
    FROM weekly2 
    group by 1,2
    )
       SELECT
       ifnull(x.weeks,y.weeks) as weeks,
       ifnull(x.validator,y.validator) as validator,
       ifnull(total_near_delegated,0) as near_staked,
       ifnull(total_near_undelegated,0) as near_unstaked,
       ifnull(total_near_delegated,0)-ifnull(total_near_undelegated,0) as total_near_delegated,
       ifnull(cumulative_near_delegated,0)-ifnull(cumulative_near_undelegated,0) as cumulative_near_delegated
       from ranking1 x
       full outer join ranking2 y on x.weeks=y.weeks and x.validator=y.validator
       where x.weeks >=current_date-INTERVAL '3 MONTHS'
    and x.validator='stakin.poolv1.near'
    """

elif selected_option == 'Atomic-nodes':
    sql2 = f"""
    WITH 
       transactions as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name IN ('deposit_and_stake')
       ),
       stakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
    FROM near.core.fact_transactions
      WHERE tx_hash in (select * from transactions)
    ),
       transactions2 as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name ='unstake_all'
       ),
       unstakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:receipt[0]:outcome:logs[0] as col,
      substring(col, CHARINDEX('Withdraw', col) + 8, CHARINDEX('NEAR', col) - CHARINDEX('Withdraw', col) - 8) as final, case when final <> '' then final/pow(10,18) else 0 end as near_unstaked
    FROM near.core.fact_transactions where tx:receipt[0]:outcome:logs[0] like 'Withdraw%'
      and tx_hash in (select * from transactions2)
    ),
    weekly as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_staked
       --amount_staked/pow(10,24) as near_staked
    FROM stakes x
       WHERE near_staked is not null 
    ),
       weekly2 as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_unstaked
       --amount_staked/pow(10,24) as near_staked
    FROM unstakes x
       WHERE near_unstaked is not null 
    ),
      totals as (
       SELECT
       x.weeks,
       sum(near_staked) as week_near_staked,
       sum(week_near_staked) over (order by x.weeks)as total_near_staked,
       sum(near_unstaked) as week_near_unstaked,
       sum(week_near_unstaked) over (order by x.weeks)as total_near_unstaked
       from weekly x
       full outer join weekly2 y on x.weeks=y.weeks
       group by 1 order by 1
       ),
       totals2 as (
       SELECT
       weeks,
       week_near_staked- week_near_unstaked as week_near_staked,
       total_near_staked-total_near_unstaked as total_near_staked
       from totals
       ),
    ranking1 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_staked) as total_near_delegated,
    sum(total_near_delegated) over (partition by validator order by weeks) as cumulative_near_delegated
    FROM weekly 
    group by 1,2
    ),
       ranking2 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_unstaked) as total_near_undelegated,
    sum(total_near_undelegated) over (partition by validator order by weeks) as cumulative_near_undelegated
    FROM weekly2 
    group by 1,2
    )
       SELECT
       ifnull(x.weeks,y.weeks) as weeks,
       ifnull(x.validator,y.validator) as validator,
       ifnull(total_near_delegated,0) as near_staked,
       ifnull(total_near_undelegated,0) as near_unstaked,
       ifnull(total_near_delegated,0)-ifnull(total_near_undelegated,0) as total_near_delegated,
       ifnull(cumulative_near_delegated,0)-ifnull(cumulative_near_undelegated,0) as cumulative_near_delegated
       from ranking1 x
       full outer join ranking2 y on x.weeks=y.weeks and x.validator=y.validator
       where x.weeks >=current_date-INTERVAL '3 MONTHS'
    and x.validator='atomic-nodes.poolv1.near'
    """

elif selected_option == 'Consensus Finoa 00':
    sql2 = f"""
    WITH 
       transactions as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name IN ('deposit_and_stake')
       ),
       stakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
    FROM near.core.fact_transactions
      WHERE tx_hash in (select * from transactions)
    ),
       transactions2 as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name ='unstake_all'
       ),
       unstakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:receipt[0]:outcome:logs[0] as col,
      substring(col, CHARINDEX('Withdraw', col) + 8, CHARINDEX('NEAR', col) - CHARINDEX('Withdraw', col) - 8) as final, case when final <> '' then final/pow(10,18) else 0 end as near_unstaked
    FROM near.core.fact_transactions where tx:receipt[0]:outcome:logs[0] like 'Withdraw%'
      and tx_hash in (select * from transactions2)
    ),
    weekly as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_staked
       --amount_staked/pow(10,24) as near_staked
    FROM stakes x
       WHERE near_staked is not null 
    ),
       weekly2 as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_unstaked
       --amount_staked/pow(10,24) as near_staked
    FROM unstakes x
       WHERE near_unstaked is not null 
    ),
      totals as (
       SELECT
       x.weeks,
       sum(near_staked) as week_near_staked,
       sum(week_near_staked) over (order by x.weeks)as total_near_staked,
       sum(near_unstaked) as week_near_unstaked,
       sum(week_near_unstaked) over (order by x.weeks)as total_near_unstaked
       from weekly x
       full outer join weekly2 y on x.weeks=y.weeks
       group by 1 order by 1
       ),
       totals2 as (
       SELECT
       weeks,
       week_near_staked- week_near_unstaked as week_near_staked,
       total_near_staked-total_near_unstaked as total_near_staked
       from totals
       ),
    ranking1 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_staked) as total_near_delegated,
    sum(total_near_delegated) over (partition by validator order by weeks) as cumulative_near_delegated
    FROM weekly 
    group by 1,2
    ),
       ranking2 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_unstaked) as total_near_undelegated,
    sum(total_near_undelegated) over (partition by validator order by weeks) as cumulative_near_undelegated
    FROM weekly2 
    group by 1,2
    )
       SELECT
       ifnull(x.weeks,y.weeks) as weeks,
       ifnull(x.validator,y.validator) as validator,
       ifnull(total_near_delegated,0) as near_staked,
       ifnull(total_near_undelegated,0) as near_unstaked,
       ifnull(total_near_delegated,0)-ifnull(total_near_undelegated,0) as total_near_delegated,
       ifnull(cumulative_near_delegated,0)-ifnull(cumulative_near_undelegated,0) as cumulative_near_delegated
       from ranking1 x
       full outer join ranking2 y on x.weeks=y.weeks and x.validator=y.validator
       where x.weeks >=current_date-INTERVAL '3 MONTHS'
    and x.validator='consensus_finoa_00.poolv1.near'
    """

elif selected_option == 'Staked':
    sql2 = f"""
    WITH 
       transactions as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name IN ('deposit_and_stake')
       ),
       stakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
    FROM near.core.fact_transactions
      WHERE tx_hash in (select * from transactions)
    ),
       transactions2 as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name ='unstake_all'
       ),
       unstakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:receipt[0]:outcome:logs[0] as col,
      substring(col, CHARINDEX('Withdraw', col) + 8, CHARINDEX('NEAR', col) - CHARINDEX('Withdraw', col) - 8) as final, case when final <> '' then final/pow(10,18) else 0 end as near_unstaked
    FROM near.core.fact_transactions where tx:receipt[0]:outcome:logs[0] like 'Withdraw%'
      and tx_hash in (select * from transactions2)
    ),
    weekly as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_staked
       --amount_staked/pow(10,24) as near_staked
    FROM stakes x
       WHERE near_staked is not null 
    ),
       weekly2 as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_unstaked
       --amount_staked/pow(10,24) as near_staked
    FROM unstakes x
       WHERE near_unstaked is not null 
    ),
      totals as (
       SELECT
       x.weeks,
       sum(near_staked) as week_near_staked,
       sum(week_near_staked) over (order by x.weeks)as total_near_staked,
       sum(near_unstaked) as week_near_unstaked,
       sum(week_near_unstaked) over (order by x.weeks)as total_near_unstaked
       from weekly x
       full outer join weekly2 y on x.weeks=y.weeks
       group by 1 order by 1
       ),
       totals2 as (
       SELECT
       weeks,
       week_near_staked- week_near_unstaked as week_near_staked,
       total_near_staked-total_near_unstaked as total_near_staked
       from totals
       ),
    ranking1 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_staked) as total_near_delegated,
    sum(total_near_delegated) over (partition by validator order by weeks) as cumulative_near_delegated
    FROM weekly 
    group by 1,2
    ),
       ranking2 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_unstaked) as total_near_undelegated,
    sum(total_near_undelegated) over (partition by validator order by weeks) as cumulative_near_undelegated
    FROM weekly2 
    group by 1,2
    )
       SELECT
       ifnull(x.weeks,y.weeks) as weeks,
       ifnull(x.validator,y.validator) as validator,
       ifnull(total_near_delegated,0) as near_staked,
       ifnull(total_near_undelegated,0) as near_unstaked,
       ifnull(total_near_delegated,0)-ifnull(total_near_undelegated,0) as total_near_delegated,
       ifnull(cumulative_near_delegated,0)-ifnull(cumulative_near_undelegated,0) as cumulative_near_delegated
       from ranking1 x
       full outer join ranking2 y on x.weeks=y.weeks and x.validator=y.validator
       where x.weeks >=current_date-INTERVAL '3 MONTHS'
    and x.validator='staked.poolv1.near'
    """

elif selected_option == 'Consensus Finoa 01':
    sql2 = f"""
    WITH 
       transactions as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name IN ('deposit_and_stake')
       ),
       stakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
    FROM near.core.fact_transactions
      WHERE tx_hash in (select * from transactions)
    ),
       transactions2 as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name ='unstake_all'
       ),
       unstakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:receipt[0]:outcome:logs[0] as col,
      substring(col, CHARINDEX('Withdraw', col) + 8, CHARINDEX('NEAR', col) - CHARINDEX('Withdraw', col) - 8) as final, case when final <> '' then final/pow(10,18) else 0 end as near_unstaked
    FROM near.core.fact_transactions where tx:receipt[0]:outcome:logs[0] like 'Withdraw%'
      and tx_hash in (select * from transactions2)
    ),
    weekly as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_staked
       --amount_staked/pow(10,24) as near_staked
    FROM stakes x
       WHERE near_staked is not null 
    ),
       weekly2 as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_unstaked
       --amount_staked/pow(10,24) as near_staked
    FROM unstakes x
       WHERE near_unstaked is not null 
    ),
      totals as (
       SELECT
       x.weeks,
       sum(near_staked) as week_near_staked,
       sum(week_near_staked) over (order by x.weeks)as total_near_staked,
       sum(near_unstaked) as week_near_unstaked,
       sum(week_near_unstaked) over (order by x.weeks)as total_near_unstaked
       from weekly x
       full outer join weekly2 y on x.weeks=y.weeks
       group by 1 order by 1
       ),
       totals2 as (
       SELECT
       weeks,
       week_near_staked- week_near_unstaked as week_near_staked,
       total_near_staked-total_near_unstaked as total_near_staked
       from totals
       ),
    ranking1 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_staked) as total_near_delegated,
    sum(total_near_delegated) over (partition by validator order by weeks) as cumulative_near_delegated
    FROM weekly 
    group by 1,2
    ),
       ranking2 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_unstaked) as total_near_undelegated,
    sum(total_near_undelegated) over (partition by validator order by weeks) as cumulative_near_undelegated
    FROM weekly2 
    group by 1,2
    )
       SELECT
       ifnull(x.weeks,y.weeks) as weeks,
       ifnull(x.validator,y.validator) as validator,
       ifnull(total_near_delegated,0) as near_staked,
       ifnull(total_near_undelegated,0) as near_unstaked,
       ifnull(total_near_delegated,0)-ifnull(total_near_undelegated,0) as total_near_delegated,
       ifnull(cumulative_near_delegated,0)-ifnull(cumulative_near_undelegated,0) as cumulative_near_delegated
       from ranking1 x
       full outer join ranking2 y on x.weeks=y.weeks and x.validator=y.validator
       where x.weeks >=current_date-INTERVAL '3 MONTHS'
    and x.validator='consensus_finoa_01.poolv1.near'
    """

elif selected_option == 'Openshards':
    sql2 = f"""
    WITH 
       transactions as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name IN ('deposit_and_stake')
       ),
       stakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
    FROM near.core.fact_transactions
      WHERE tx_hash in (select * from transactions)
    ),
       transactions2 as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name ='unstake_all'
       ),
       unstakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:receipt[0]:outcome:logs[0] as col,
      substring(col, CHARINDEX('Withdraw', col) + 8, CHARINDEX('NEAR', col) - CHARINDEX('Withdraw', col) - 8) as final, case when final <> '' then final/pow(10,18) else 0 end as near_unstaked
    FROM near.core.fact_transactions where tx:receipt[0]:outcome:logs[0] like 'Withdraw%'
      and tx_hash in (select * from transactions2)
    ),
    weekly as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_staked
       --amount_staked/pow(10,24) as near_staked
    FROM stakes x
       WHERE near_staked is not null 
    ),
       weekly2 as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_unstaked
       --amount_staked/pow(10,24) as near_staked
    FROM unstakes x
       WHERE near_unstaked is not null 
    ),
      totals as (
       SELECT
       x.weeks,
       sum(near_staked) as week_near_staked,
       sum(week_near_staked) over (order by x.weeks)as total_near_staked,
       sum(near_unstaked) as week_near_unstaked,
       sum(week_near_unstaked) over (order by x.weeks)as total_near_unstaked
       from weekly x
       full outer join weekly2 y on x.weeks=y.weeks
       group by 1 order by 1
       ),
       totals2 as (
       SELECT
       weeks,
       week_near_staked- week_near_unstaked as week_near_staked,
       total_near_staked-total_near_unstaked as total_near_staked
       from totals
       ),
    ranking1 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_staked) as total_near_delegated,
    sum(total_near_delegated) over (partition by validator order by weeks) as cumulative_near_delegated
    FROM weekly 
    group by 1,2
    ),
       ranking2 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_unstaked) as total_near_undelegated,
    sum(total_near_undelegated) over (partition by validator order by weeks) as cumulative_near_undelegated
    FROM weekly2 
    group by 1,2
    )
       SELECT
       ifnull(x.weeks,y.weeks) as weeks,
       ifnull(x.validator,y.validator) as validator,
       ifnull(total_near_delegated,0) as near_staked,
       ifnull(total_near_undelegated,0) as near_unstaked,
       ifnull(total_near_delegated,0)-ifnull(total_near_undelegated,0) as total_near_delegated,
       ifnull(cumulative_near_delegated,0)-ifnull(cumulative_near_undelegated,0) as cumulative_near_delegated
       from ranking1 x
       full outer join ranking2 y on x.weeks=y.weeks and x.validator=y.validator
       where x.weeks >=current_date-INTERVAL '3 MONTHS'
    and x.validator='openshards.poolv1.near'
    """

elif selected_option == 'Everstake':
    sql2 = f"""
     WITH 
       transactions as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name IN ('deposit_and_stake')
       ),
       stakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
    FROM near.core.fact_transactions
      WHERE tx_hash in (select * from transactions)
    ),
       transactions2 as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name ='unstake_all'
       ),
       unstakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:receipt[0]:outcome:logs[0] as col,
      substring(col, CHARINDEX('Withdraw', col) + 8, CHARINDEX('NEAR', col) - CHARINDEX('Withdraw', col) - 8) as final, case when final <> '' then final/pow(10,18) else 0 end as near_unstaked
    FROM near.core.fact_transactions where tx:receipt[0]:outcome:logs[0] like 'Withdraw%'
      and tx_hash in (select * from transactions2)
    ),
    weekly as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_staked
       --amount_staked/pow(10,24) as near_staked
    FROM stakes x
       WHERE near_staked is not null 
    ),
       weekly2 as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_unstaked
       --amount_staked/pow(10,24) as near_staked
    FROM unstakes x
       WHERE near_unstaked is not null 
    ),
      totals as (
       SELECT
       x.weeks,
       sum(near_staked) as week_near_staked,
       sum(week_near_staked) over (order by x.weeks)as total_near_staked,
       sum(near_unstaked) as week_near_unstaked,
       sum(week_near_unstaked) over (order by x.weeks)as total_near_unstaked
       from weekly x
       full outer join weekly2 y on x.weeks=y.weeks
       group by 1 order by 1
       ),
       totals2 as (
       SELECT
       weeks,
       week_near_staked- week_near_unstaked as week_near_staked,
       total_near_staked-total_near_unstaked as total_near_staked
       from totals
       ),
    ranking1 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_staked) as total_near_delegated,
    sum(total_near_delegated) over (partition by validator order by weeks) as cumulative_near_delegated
    FROM weekly 
    group by 1,2
    ),
       ranking2 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_unstaked) as total_near_undelegated,
    sum(total_near_undelegated) over (partition by validator order by weeks) as cumulative_near_undelegated
    FROM weekly2 
    group by 1,2
    )
       SELECT
       ifnull(x.weeks,y.weeks) as weeks,
       ifnull(x.validator,y.validator) as validator,
       ifnull(total_near_delegated,0) as near_staked,
       ifnull(total_near_undelegated,0) as near_unstaked,
       ifnull(total_near_delegated,0)-ifnull(total_near_undelegated,0) as total_near_delegated,
       ifnull(cumulative_near_delegated,0)-ifnull(cumulative_near_undelegated,0) as cumulative_near_delegated
       from ranking1 x
       full outer join ranking2 y on x.weeks=y.weeks and x.validator=y.validator
       where x.weeks >=current_date-INTERVAL '3 MONTHS'
    and x.validator='everstake.poolv1.near'
    """

else:
    sql2 = f"""
    WITH 
       transactions as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name IN ('deposit_and_stake')
       ),
       stakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
    FROM near.core.fact_transactions
      WHERE tx_hash in (select * from transactions)
    ),
       transactions2 as (
       SELECT tx_hash
    FROM near.core.fact_actions_events_function_call
      WHERE method_name ='unstake_all'
       ),
       unstakes as (
    SELECT 
      block_timestamp,
      tx_hash as tx,
      tx_receiver as validator, 
      tx_signer as delegator,
      tx:receipt[0]:outcome:logs[0] as col,
      substring(col, CHARINDEX('Withdraw', col) + 8, CHARINDEX('NEAR', col) - CHARINDEX('Withdraw', col) - 8) as final, case when final <> '' then final/pow(10,18) else 0 end as near_unstaked
    FROM near.core.fact_transactions where tx:receipt[0]:outcome:logs[0] like 'Withdraw%'
      and tx_hash in (select * from transactions2)
    ),
    weekly as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_staked
       --amount_staked/pow(10,24) as near_staked
    FROM stakes x
       WHERE near_staked is not null 
    ),
       weekly2 as (
       SELECT 
       trunc(x.block_timestamp,'week') as weeks,
       x.tx,
       x.validator,
       near_unstaked
       --amount_staked/pow(10,24) as near_staked
    FROM unstakes x
       WHERE near_unstaked is not null 
    ),
      totals as (
       SELECT
       x.weeks,
       sum(near_staked) as week_near_staked,
       sum(week_near_staked) over (order by x.weeks)as total_near_staked,
       sum(near_unstaked) as week_near_unstaked,
       sum(week_near_unstaked) over (order by x.weeks)as total_near_unstaked
       from weekly x
       full outer join weekly2 y on x.weeks=y.weeks
       group by 1 order by 1
       ),
       totals2 as (
       SELECT
       weeks,
       week_near_staked- week_near_unstaked as week_near_staked,
       total_near_staked-total_near_unstaked as total_near_staked
       from totals
       ),
    ranking1 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_staked) as total_near_delegated,
    sum(total_near_delegated) over (partition by validator order by weeks) as cumulative_near_delegated
    FROM weekly 
    group by 1,2
    ),
       ranking2 as (
       SELECT 
       weeks,
       validator,
       count(distinct tx) as txs,
       sum(near_unstaked) as total_near_undelegated,
    sum(total_near_undelegated) over (partition by validator order by weeks) as cumulative_near_undelegated
    FROM weekly2 
    group by 1,2
    )
       SELECT
       ifnull(x.weeks,y.weeks) as weeks,
       ifnull(x.validator,y.validator) as validator,
       ifnull(total_near_delegated,0) as near_staked,
       ifnull(total_near_undelegated,0) as near_unstaked,
       ifnull(total_near_delegated,0)-ifnull(total_near_undelegated,0) as total_near_delegated,
       ifnull(cumulative_near_delegated,0)-ifnull(cumulative_near_undelegated,0) as cumulative_near_delegated
       from ranking1 x
       full outer join ranking2 y on x.weeks=y.weeks and x.validator=y.validator
       where x.weeks >=current_date-INTERVAL '3 MONTHS'
    """

     
results2 = compute(sql2)
df2 = pd.DataFrame(results2.records)      
         
         
st.write('')
st.write('')
base2=alt.Chart(df2).encode(x=alt.X('weeks:O', axis=alt.Axis(labelAngle=325)))
line1=base2.mark_line(color='blue').encode(y=alt.Y('sum(near_staked):Q', axis=alt.Axis(grid=True)))
line2=base2.mark_line(color='orange').encode(y='sum(near_unstaked):Q')
st.altair_chart((line1 + line2).properties(title='Weekly NEAR staked vs unstaked over the past 3 months',width=1200))


# In[24]:


st.altair_chart(alt.Chart(df2, height=500, width=1200)
    .mark_bar(color='green')
    .encode(x='weeks:O', y='sum(total_near_delegated):Q')
    .properties(title='Weekly net NEAR staked over the past 3 months'))


# In[16]:


st.altair_chart(alt.Chart(df2, height=500, width=1200)
    .mark_bar()
    .encode(x='weeks:O', y='total_near_delegated:Q',color=alt.Color('validator', scale=alt.Scale(scheme='dark2')))
    .properties(title='Weekly net NEAR staked by chosen validator'))
         
         


# In[41]:


st.subheader("Near Nakamoto Coefficient over the past 3 months")
st.markdown('To close this analysis, here it can be seen a representation of the current total NEAR staked by each validator as well as the evolution of the Nakamoto Coefficient.')
st.markdown('**Nakamoto Coefficient** is one of the main interesting metrics to measure the decentralization of a blockchain, that represents how many validators are needed to accumulate more than 50% of the total current NEAR staked.')
sql3='''
 WITH 
   transactions as (
   SELECT tx_hash
FROM near.core.fact_actions_events_function_call
  WHERE method_name IN ('deposit_and_stake')
   ),
   stakes as (
SELECT 
  block_timestamp,
  tx_hash as tx,
  tx_receiver as validator, 
  tx_signer as delegator,
  tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
FROM near.core.fact_transactions
  WHERE tx_hash in (select * from transactions)
),
   transactions2 as (
   SELECT tx_hash
FROM near.core.fact_actions_events_function_call
  WHERE method_name ='unstake_all'
   ),
   unstakes as (
SELECT 
  block_timestamp,
  tx_hash as tx,
  tx_receiver as validator, 
  tx_signer as delegator,
  tx:actions[0]:FunctionCall:deposit/pow(10,24) near_unstaked
FROM near.core.fact_transactions
  WHERE tx_hash in (select * from transactions2)
),
weekly as (
   SELECT 
   trunc(x.block_timestamp,'week') as weeks,
   x.tx,
   x.validator,
   near_staked
   --amount_staked/pow(10,24) as near_staked
FROM stakes x
   WHERE near_staked is not null 
),
   weekly2 as (
   SELECT 
   trunc(x.block_timestamp,'week') as weeks,
   x.tx,
   x.validator,
   near_unstaked
   --amount_staked/pow(10,24) as near_staked
FROM unstakes x
   WHERE near_unstaked is not null 
),
  totals as (
   SELECT
   x.weeks,
   sum(near_staked) as week_near_staked,
   sum(week_near_staked) over (order by x.weeks)as total_near_staked,
   sum(near_unstaked) as week_near_unstaked,
   sum(week_near_unstaked) over (order by x.weeks)as total_near_unstaked
   from weekly x
   full outer join weekly2 y on x.weeks=y.weeks
   group by 1 order by 1
   ),
   totals2 as (
   SELECT
   weeks,
   week_near_staked- week_near_unstaked as week_near_staked,
   total_near_staked-total_near_unstaked as total_near_staked
   from totals
   ),
ranking1 as (
   SELECT 
   weeks,
   validator,
   count(distinct tx) as txs,
   sum(near_staked) as total_near_delegated,
sum(total_near_delegated) over (partition by validator order by weeks) as cumulative_near_delegated
FROM weekly 
group by 1,2
),
   ranking2 as (
   SELECT 
   weeks,
   validator,
   count(distinct tx) as txs,
   sum(near_unstaked) as total_near_undelegated,
sum(total_near_undelegated) over (partition by validator order by weeks) as cumulative_near_undelegated
FROM weekly2 
group by 1,2
),
   ranking3 as (
   SELECT
   ifnull(x.weeks,y.weeks) as weeks,
   ifnull(x.validator,y.validator) as validator,
   ifnull(total_near_delegated,0)-ifnull(total_near_undelegated,0) as total_near_delegated,
   ifnull(cumulative_near_delegated,0)-ifnull(cumulative_near_undelegated,0) as cumulative_near_delegated
   from ranking1 x
   full outer join ranking2 y on x.weeks=y.weeks and x.validator=y.validator
   ),
stats as (
  SELECT
  weeks,
33 as bizantine_fault_tolerance,
total_near_staked,
(total_near_staked*bizantine_fault_tolerance)/100 as threshold--,
--sum(total_sol_delegated) over (partition by weeks order by validator_ranks asc) as total_sol_delegated_by_ranks,
--count(distinct vote_accounts) as validators
from totals2
), 
stats2 as (
   select *,
1 as numbering,
sum(numbering) over (partition by weeks order by cumulative_near_delegated desc) as rank 
from ranking3
   )
SELECT
weeks,
validator,
cumulative_near_delegated,
rank,
sum(cumulative_near_delegated) over (partition by weeks order by rank asc) as total_staked
--count(case when total_staked)
--sum(1) over (partition by weeks order by stake_rank) as nakamoto_coeff
  from stats2 where cumulative_near_delegated is not null and weeks>=CURRENT_DATE-6 and rank<100
order by rank asc


'''


# In[42]:

results3 = compute(sql3)
df3 = pd.DataFrame(results3.records)


# In[44]:


st.altair_chart(alt.Chart(df3, height=500, width=1200)
    .mark_bar()
    .encode(x=alt.X('validator',sort='-y'), y=('cumulative_near_delegated'),color=alt.Color('cumulative_near_delegated'))
    .properties(title='Current NEAR delegated by validator'))


# In[31]:


sql4='''
 WITH 
   transactions as (
   SELECT tx_hash
FROM near.core.fact_actions_events_function_call
  WHERE method_name IN ('deposit_and_stake')
   ),
   stakes as (
SELECT 
  block_timestamp,
  tx_hash as tx,
  tx_receiver as validator, 
  tx_signer as delegator,
  tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
FROM near.core.fact_transactions
  WHERE tx_hash in (select * from transactions)
),
weekly as (
   SELECT 
   trunc(block_timestamp,'week') as weeks,
   tx,
   validator,
   near_staked
   --amount_staked/pow(10,24) as near_staked
FROM stakes WHERE near_staked is not null 
),
  totals as (
   SELECT
   weeks,
   sum(near_staked) as week_near_staked,
   sum(week_near_staked) over (order by weeks)as total_near_staked
   from weekly
   group by 1 order by 1
   ),
ranking as (
   SELECT 
   weeks,
   validator,
   count(distinct tx) as txs,
   sum(near_staked) as total_near_delegated,
sum(total_near_delegated) over (partition by validator order by weeks) as cumulative_near_delegated
FROM weekly 
group by 1,2
),
stats as (
  SELECT
  weeks,
50 as bizantine_fault_tolerance,
total_near_staked,
(total_near_staked*bizantine_fault_tolerance)/100 as threshold--,
--sum(total_sol_delegated) over (partition by weeks order by validator_ranks asc) as total_sol_delegated_by_ranks,
--count(distinct vote_accounts) as validators
from totals
), 
stats2 as (
   select *,
1 as numbering,
sum(numbering) over (partition by weeks order by cumulative_near_delegated desc) as rank 
from ranking
   ),
stats3 as (
SELECT
weeks,
validator,
cumulative_near_delegated,
rank,
sum(cumulative_near_delegated) over (partition by weeks order by rank asc) as total_staked
--count(case when total_staked)
--sum(1) over (partition by weeks order by stake_rank) as nakamoto_coeff
  from stats2
order by rank asc),
   final_nak as (
SELECT
a.weeks,
validator,
count(case when total_staked <= threshold then 1 end) as nakamoto_coeff
from stats3 a 
join stats b 
on a.weeks = b.weeks where a.weeks >=CURRENT_DATE-INTERVAL '3 MONTHS' and a.weeks<current_date-1
group by 1,2
order by 1 asc
   )
SELECT
weeks,sum(nakamoto_coeff) as nakamoto_coeff
from final_nak
group by 1 order by 1 asc 
'''


# In[32]:

results4 = compute(sql4)
df4 = pd.DataFrame(results4.records)


# In[33]:


st.altair_chart(alt.Chart(df4, height=500, width=1200)
    .mark_bar()
    .encode(x='weeks:N', y='nakamoto_coeff:Q',color=alt.Color('nakamoto_coeff'))
    .properties(title='Weekly Nakamoto Coefficient over the past 3 months'))


# In[ ]:






# In[ ]:


st.subheader('Conclusions')
st.write('Overall, the major of the actions (more than 60%) are “deposit and stake” actions. Followed by unstake actions like “unstake” or “unstake_all”. However, the unstaking actions has increased over the past months.')
st.write('The top 10 validators holdings reduced from almost 60% of total staked NEAR to around 55%.')
st.write('The amount of NEAR staked increased over the past 3 months. However, the situation is not similar of the amount of active validators.')
st.write('After these past 3 months, the Nakamoto coefficient continued at a level of 11. It is good because the amount of needed validators to halt the blockchain remains above 10, but it shows no improvements on the Near decentralization.')
st.write('The amount of NEAR staked experimented an uptrend from around 52M of NEAR staked to 55M staked.')
st.write('The amount of staking actions and the amount of delegators that this pools are capting decreased over the last months.')
st.markdown('This app has been done by **_Adrià Parcerisas_**, a PhD Biomedical Engineer related to Machine Learning and Artificial intelligence technical projects for data analysis and research, as well as dive deep on-chain data analysis about cryptocurrency projects. You can find me on [Twitter](https://twitter.com/adriaparcerisas)')
st.write('')
st.markdown('The full sources used to develop this app can be found to the following link: [Github link](https://github.com/adriaparcerisas/Near-developer-activity)')
st.markdown('_Powered by [Flipside Crypto](https://flipsidecrypto.xyz) and [MetricsDAO](https://metricsdao.notion.site)_')

