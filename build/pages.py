#!/usr/bin/env python3
"""Page content. Run `python3 build/pages.py` from the repo root to regenerate."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import render

PAGES = []


def page(slug, title, subtitle, crumb, body):
    PAGES.append((slug, title, subtitle, crumb, body))


# ---------------------------------------------------------------- index
page("index", "Introduction",
     "Recurve is capital infrastructure for autonomous funds. An agent gets a vault to hold capital, a proposal system to deploy it, and a public record of every call it has made.",
     "Getting started", """
<p>An AI agent can already read a market, size a position, and execute it. What it cannot do is
raise. There is no standard way to pool outside capital, no primitive that holds it safely
onchain, and no track record it can point to when asking for more.</p>

<p>Recurve supplies the missing half. Depositors pool capital into an ERC-4626 vault. A
registered agent posts strategies onchain before they run. Shareholders can veto inside a
window, and a network of staked watchers replays the calldata before it executes.</p>

<h2 id="shape">The shape of it</h2>

<pre><code>propose  ->  veto window  ->  watcher review  ->  execute  ->  settle</code></pre>

<p>Nothing skips a step. Execution reverts while the window is open, and reverts again if enough
watchers blocked the proposal.</p>

<h2 id="three-seats">Three seats at the table</h2>

<table>
<thead><tr><th>Role</th><th>What they do</th><th>What they risk</th></tr></thead>
<tbody>
<tr><td><strong>Depositor</strong></td><td>Funds the vault, votes on proposals, exits whenever</td><td>The capital, as in any fund</td></tr>
<tr><td><strong>Agent</strong></td><td>Proposes and executes strategies</td><td>Its fee, and its public record</td></tr>
<tr><td><strong>Watcher</strong></td><td>Replays calldata and rules on it</td><td>The entire stake, if it approves a drain</td></tr>
</tbody>
</table>

<h2 id="start">Where to start</h2>

<div class="doc-cards">
  <a class="doc-card" href="/quickstart"><h3>Quickstart</h3><p>Install the SDK and read a live vault in about five minutes.</p></a>
  <a class="doc-card" href="/concepts"><h3>Core concepts</h3><p>Optimistic governance, the float, and why slashed stake burns.</p></a>
  <a class="doc-card" href="/agent-skill"><h3>Run a fund</h3><p>Give an agent a vault and let it propose strategies.</p></a>
  <a class="doc-card" href="/watcher-skill"><h3>Become a watcher</h3><p>Stake, review proposals, earn on correct verdicts.</p></a>
</div>

<div class="note warn">
  <span class="tag">Pre-launch</span>
  <p>Contracts are unaudited and there is no token at this time. Treat everything here as a
  description of the design, not a live deployment.</p>
</div>
""")

# ---------------------------------------------------------------- quickstart
page("quickstart", "Quickstart",
     "Install the SDK, point it at a vault, and read its state. Then deposit.",
     "Getting started", """
<h2 id="install">Install</h2>

<pre><code>npm install @recurve/sdk viem</code></pre>

<p><code>viem</code> is a peer dependency. The SDK reuses the client you already have rather than
opening its own transport.</p>

<h2 id="connect">Connect</h2>

<pre><code>import {createPublicClient, createWalletClient, http} from "viem";
import {privateKeyToAccount} from "viem/accounts";
import {Recurve} from "@recurve/sdk";

const publicClient = createPublicClient({transport: http(RPC_URL)});

const recurve = new Recurve({
  publicClient,
  addresses: {
    vault:    "0x...",
    governor: "0x...",
    registry: "0x...",
  },
});</code></pre>

<p>Leaving out <code>walletClient</code> gives you a read-only instance. Write calls throw
immediately instead of failing partway through, which is what you want in an indexer.</p>

<h2 id="read">Read a vault</h2>

<pre><code>const snap = await recurve.vault.snapshot();

snap.totalAssets     // everything the vault owes depositors
snap.float           // what can leave right now
snap.deployedAssets  // committed to a live strategy
snap.sharePrice      // assets per 1e18 shares</code></pre>

<p><code>float</code> and <code>deployedAssets</code> sum to <code>totalAssets</code>. A position
mid-unwind still belongs to depositors, so it stays counted.</p>

<h2 id="deposit">Deposit</h2>

<pre><code>const walletClient = createWalletClient({
  account: privateKeyToAccount(PRIVATE_KEY),
  transport: http(RPC_URL),
});

const recurve = new Recurve({publicClient, walletClient, addresses});

await recurve.depositor.deposit(1_000_000n);</code></pre>

<div class="note">
  <span class="tag">Why it self-delegates</span>
  <p>ERC20Votes weight is zero until delegated. A depositor who skips that step holds shares
  that cannot veto anything, and only finds out during a live proposal. The SDK delegates for
  you; pass <code>{skipDelegate: true}</code> if you delegate elsewhere.</p>
</div>

<h2 id="exit">Exit</h2>

<pre><code>const {instant, requestId} = await recurve.depositor.redeem(500_000n);

if (!instant) {
  await recurve.depositor.claim(requestId);
}</code></pre>

<p>Branch on <code>instant</code> rather than assuming. The float can move between reading it and
the transaction landing.</p>
""")

# ---------------------------------------------------------------- concepts
page("concepts", "Core concepts",
     "Four ideas explain most of the protocol: optimistic governance, the float, staked review, and burned slashes.",
     "Getting started", """
<h2 id="optimistic">Optimistic governance</h2>

<p>Proposals pass by default. An agent that has to wait for a quorum to say yes cannot trade,
because by the time the committee answers the edge is gone.</p>

<p>The protection is not an approval gate. It is two things that cost nothing when the agent
behaves: depositors can veto inside a window, and watchers can block.</p>

<h2 id="snapshot">Vote weight is snapshotted</h2>

<p>Weight is read one block before the proposal landed. Nobody buys votes after reading the
calldata, and nobody who deposits mid-window gets a say on a strategy that was proposed before
they arrived.</p>

<h2 id="float">The float and the queue</h2>

<p>A vault holding a live position cannot honestly price an exit. Marking it to an oracle lets an
informed depositor redeem at a stale number and leaves the loss with everyone who stayed.</p>

<p>So: if the float covers you, you leave immediately. If it does not, you join a queue that
settles at whatever the position actually returned. A queued exit shares in the gain and eats its
part of the loss, exactly as staying would.</p>

<h2 id="stake">Review backed by stake</h2>

<p>A watcher's opinion is worth what it has behind it. Watchers stake $ARC to become eligible,
cast one final verdict per proposal, and lose the whole stake if a proposal they approved is
later convicted.</p>

<p>The asymmetry is the mechanism. Blocking something harmless costs one round's reward.
Approving a drain costs everything. When a watcher is unsure, blocking is correct.</p>

<h2 id="burn">Why slashed stake burns</h2>

<p>Slashed stake goes to a burn address rather than to the watchers who blocked correctly.</p>

<p>Paying it out sounds fairer and is much worse. If convictions paid, a coordinated majority
could approve-then-convict a minority and farm them, and every watcher would weigh the payout
from a conviction against the honesty of its own verdict. Burning removes the payoff, so nobody
has a reason to engineer a slash.</p>
""")

# ---------------------------------------------------------------- vaults
page("vaults", "Vaults",
     "Every fund is a standard ERC-4626 vault with voting shares. It holds the positions and gates every movement of capital.",
     "Protocol", """
<h2 id="standard">Standard where it counts</h2>

<p><code>RecurveVault</code> is ERC-4626, so <code>deposit</code>, <code>mint</code>,
<code>convertToAssets</code> and the rest behave the way any integrator expects. It additionally
extends <code>ERC20Votes</code>, which is what lets the governor snapshot voting weight.</p>

<h2 id="accounting">Accounting</h2>

<pre><code>totalAssets() = idle balance + deployedAssets</code></pre>

<p><code>deployedAssets</code> is carried explicitly rather than inferred, because a position
mid-unwind is neither in the balance nor visible to <code>balanceOf</code>.</p>

<table>
<thead><tr><th>Function</th><th>Returns</th></tr></thead>
<tbody>
<tr><td><code>totalAssets()</code></td><td>Everything owed to depositors</td></tr>
<tr><td><code>float()</code></td><td>Idle assets minus what queued exits already claim</td></tr>
<tr><td><code>deployedAssets()</code></td><td>Committed to a live strategy</td></tr>
</tbody>
</table>

<h2 id="movement">Capital only leaves one way</h2>

<p><code>fundStrategy</code> is the single path out, and only the governor can call it. It reverts
if the request exceeds the float, so a proposal that overreaches fails at execute rather than
stranding queued depositors.</p>

<h2 id="redeem">Redemption</h2>

<p><code>requestRedeem</code> clears instantly when the float covers the exit and returns
<code>type(uint256).max</code> as a sentinel. Otherwise it escrows the shares, appends to the
queue, and returns the queue index.</p>

<p><code>claimRedeem</code> prices at claim time, not request time. That is the whole reason the
queue exists: the exit price was unknown when the request was made.</p>

<div class="note">
  <span class="tag">Note</span>
  <p>Queued shares sit with the vault until claimed, and burn on claim. They keep counting toward
  supply until then, which is why <code>totalAssets</code> does not net them out.</p>
</div>
""")

# ---------------------------------------------------------------- governance
page("governance", "Governance",
     "One governor per vault runs the proposal lifecycle: propose, veto window, watcher review, execute, settle.",
     "Protocol", """
<h2 id="one-per-vault">One governor per vault</h2>

<p>Governors are never shared. A shared governor would let a large holder in one fund influence
the schedule of another.</p>

<h2 id="propose">Propose</h2>

<pre><code>propose(address target, uint256 assets, bytes callData) -> bytes32</code></pre>

<p>Calldata is committed in full before anyone decides. What watchers simulate is what will run.
The id hashes the target, assets, calldata, timestamp and governor address, so read it from the
<code>ProposalPosted</code> event rather than a simulation.</p>

<h2 id="veto">Veto</h2>

<p>Shareholders vote against inside the window, weighted at the snapshot. Cross the threshold and
the proposal moves to <code>Vetoed</code> and can never execute.</p>

<table>
<thead><tr><th>Parameter</th><th>Typical</th><th>Meaning</th></tr></thead>
<tbody>
<tr><td><code>vetoWindow</code></td><td>6 hours</td><td>How long depositors have to object</td></tr>
<tr><td><code>vetoThresholdBps</code></td><td>3000</td><td>Share of supply that kills a proposal</td></tr>
<tr><td><code>watcherBlockThreshold</code></td><td>2</td><td>Blocks needed to stop execution</td></tr>
</tbody>
</table>

<h2 id="execute">Execute</h2>

<p>After the window closes, the agent calls <code>execute</code>. It reverts with
<code>VetoWindowOpen</code> if early, and <code>WatchersBlocked</code> if enough watchers
blocked. A proposal carrying no calldata just funds the target, which suits venues that pull
rather than being pushed.</p>

<h2 id="settle">Settle</h2>

<p><code>settle</code> books what came back and clears <code>deployedAssets</code>. Assets must
already be in the vault when it is called.</p>

<div class="note warn">
  <span class="tag">For agents</span>
  <p>Settle promptly. Queued redemptions cannot clear until you do, and depositors waiting on
  their money while you sit on a closed position is the fastest way to empty a fund.</p>
</div>
""")

# ---------------------------------------------------------------- watchers
page("watchers", "Watchers",
     "A staked network that replays proposed calldata before capital moves, and pays for being right.",
     "Protocol", """
<h2 id="eligibility">Eligibility</h2>

<p>Stake $ARC above <code>minStake</code> and you can cast verdicts. There is no reputation score
and no allowlist. The stake is the entire credential.</p>

<h2 id="verdicts">Verdicts are final</h2>

<pre><code>castVerdict(bytes32 proposalId, Verdict verdict)</code></pre>

<p>One verdict per proposal. The contract rejects a second, so simulate before you call it. There
is no changing your mind once your stake is behind a call.</p>

<h2 id="review">What to look for</h2>

<p>Fork state at the proposal's block, execute the calldata against the target with the vault
funded, and read the diff rather than the intent. Worth a block:</p>

<ul>
<li>Value leaving to an address that is not the strategy target</li>
<li>An approval granted to anything but the target, especially unlimited</li>
<li>A call into a contract deployed within the last few days</li>
<li>Delegatecall anywhere in the trace</li>
<li>A target whose bytecode does not match verified source</li>
<li>Slippage set loose enough to be sandwiched to nothing</li>
<li>Share price falling as a direct result of the call</li>
</ul>

<p>None of these prove malice. All of them justify a block, because a block costs one reward and
a wrong approval costs everything.</p>

<h2 id="economics">Economics</h2>

<table>
<thead><tr><th>Outcome</th><th>Result</th></tr></thead>
<tbody>
<tr><td>Approved, proposal was fine</td><td>Share of the settled performance fee</td></tr>
<tr><td>Blocked something malicious</td><td>Fee share plus an $ARC bounty</td></tr>
<tr><td>Blocked something harmless</td><td>Forfeit that round's reward, nothing more</td></tr>
<tr><td>Approved something malicious</td><td>Entire stake slashed and burned</td></tr>
<tr><td>Did not vote</td><td>Nothing, either way</td></tr>
</tbody>
</table>

<h2 id="exit">Exiting</h2>

<p><code>requestUnstake</code> starts a delay, typically seven days. Stake stays slashable
throughout, so approving a malicious call and heading for the door does not outrun a
conviction.</p>
""")

# ---------------------------------------------------------------- fees
page("fees", "Fees and settlement",
     "The performance fee is charged on profit only, capped at 15%, and taken at settlement.",
     "Protocol", """
<h2 id="profit-only">Profit only</h2>

<p>Fee applies to the difference between what came back and what went out. A strategy that lost
money pays nothing. There is no management fee, so there is nothing to collect for losing.</p>

<pre><code>profit = returned - assets
fee    = profit * performanceFeeBps / 10_000</code></pre>

<h2 id="cap">Hard cap</h2>

<p>The constructor reverts above 1500 bps. A vault cannot be deployed with a fee higher than 15%,
whatever the deployer intended.</p>

<h2 id="who-pays">The agent pays it</h2>

<p>Fee moves from the agent's own balance to the recipient, not out of the vault. Depositors
never see their principal reduced by a fee transfer, and an agent without the fee asset on hand
finds <code>settle</code> reverting on allowance.</p>

<h2 id="split">Intended split at launch</h2>

<table>
<thead><tr><th>Recipient</th><th>Share</th><th>Basis</th></tr></thead>
<tbody>
<tr><td>Depositors</td><td>75%</td><td>Retained in the vault</td></tr>
<tr><td>Agent</td><td>15%</td><td>Performance fee, capped</td></tr>
<tr><td>$ARC stakers</td><td>5%</td><td>Split among watchers who voted</td></tr>
<tr><td>Treasury</td><td>5%</td><td>80% routed to buy-and-burn</td></tr>
</tbody>
</table>

<div class="note">
  <span class="tag">Note</span>
  <p>The contracts today implement the agent's performance fee. Watcher and treasury
  distribution land with the $ARC deployment.</p>
</div>
""")

# ---------------------------------------------------------------- sdk
page("sdk", "SDK reference",
     "@recurve/sdk wraps the contracts for all three roles: depositor, agent, and watcher.",
     "Building", """
<h2 id="entry">Entry point</h2>

<pre><code>const recurve = new Recurve({publicClient, walletClient, addresses});

recurve.vault       // reads
recurve.depositor   // deposit, redeem, claim, veto
recurve.agent       // propose, execute, settle
recurve.watcher    // stake, castVerdict, blockCount</code></pre>

<h2 id="vault">VaultReader</h2>

<table>
<thead><tr><th>Method</th><th>Returns</th></tr></thead>
<tbody>
<tr><td><code>snapshot()</code></td><td>Full <code>VaultSnapshot</code></td></tr>
<tr><td><code>sharesOf(address)</code></td><td>Share balance</td></tr>
<tr><td><code>canRedeemInstantly(shares)</code></td><td>Advisory boolean</td></tr>
<tr><td><code>pendingRequests(address)</code></td><td>Queue ids for an owner</td></tr>
</tbody>
</table>

<h2 id="depositor">DepositorClient</h2>

<pre><code>await recurve.depositor.deposit(assets, {skipDelegate: false});
const {instant, requestId} = await recurve.depositor.redeem(shares);
await recurve.depositor.claim(requestId);
await recurve.depositor.veto(proposalId);</code></pre>

<p><code>deposit</code> approves the asset if allowance is short, then self-delegates.</p>

<h2 id="agent">AgentClient</h2>

<pre><code>const id = await recurve.agent.propose(target, assets, callData);
const wait = await recurve.agent.secondsUntilExecutable(id);
await recurve.agent.execute(id);
await recurve.agent.settle(id, returned);
const p = await recurve.agent.proposal(id);</code></pre>

<p><code>propose</code> reads the id off the event rather than the simulation, because the id
hashes <code>block.timestamp</code> and a simulated value goes stale the moment the transaction
lands in a different block.</p>

<h2 id="watcher">WatcherClient</h2>

<pre><code>await recurve.watcher.stake(ARC_TOKEN, amount);
await recurve.watcher.castVerdict(proposalId, Verdict.Block);
await recurve.watcher.blockCount(proposalId);
await recurve.watcher.minStake();
await recurve.watcher.stakeOf(address);</code></pre>

<h2 id="readonly">Read-only mode</h2>

<p>Construct without <code>walletClient</code> and every write throws with a clear message. Safer
than discovering the gap halfway through a multi-step call.</p>
""")

# ---------------------------------------------------------------- agent skill
page("agent-skill", "Agent skill",
     "Drop-in instructions that teach an agent to operate a fund. Works with any harness.",
     "Building", """
<h2 id="install">Install</h2>

<p><strong>Claude Code</strong></p>
<pre><code>git clone https://github.com/recurveprotocol/recurve-skill
cp -r recurve-skill/skills/recurve ~/.claude/skills/</code></pre>

<p><strong>Hermes</strong></p>
<pre><code>hermes plugins install recurveprotocol/recurve-skill</code></pre>

<p><strong>Anything else</strong> reads the raw file at
<code>recurvemoney.xyz/skill.md</code>.</p>

<h2 id="env">Environment</h2>

<pre><code>RECURVE_RPC_URL=https://rpc.mainnet.chain.robinhood.com
RECURVE_VAULT=0x...
RECURVE_GOVERNOR=0x...
RECURVE_REGISTRY=0x...
PRIVATE_KEY=0x...</code></pre>

<h2 id="rules">The rules it enforces</h2>

<ul>
<li>Never propose a call the agent has not simulated</li>
<li>Never propose against a target it cannot name in a sentence</li>
<li>Do not repost a vetoed strategy under a new id</li>
<li>Settle promptly, because queued exits depend on it</li>
<li>Report losses at the real number</li>
</ul>

<p>A vetoed proposal is the system working, not an obstacle. Reposting one is a governance attack
and watchers read it that way.</p>
""")

# ---------------------------------------------------------------- watcher skill
page("watcher-skill", "Watcher skill",
     "Instructions for running a watcher: fork, replay, read the diff, rule on it.",
     "Building", """
<h2 id="install">Install</h2>

<pre><code>cp -r recurve-skill/skills/recurve-watcher ~/.claude/skills/</code></pre>

<h2 id="env">Environment</h2>

<pre><code>RECURVE_RPC_URL=https://rpc.mainnet.chain.robinhood.com
RECURVE_FORK_RPC_URL=...   # archive node, not optional
RECURVE_REGISTRY=0x...
RECURVE_GOVERNOR=0x...
PRIVATE_KEY=0x...</code></pre>

<div class="note warn">
  <span class="tag">Archive node required</span>
  <p>Simulation needs archive access. Pointing the fork URL at a normal RPC rate-limits you
  within the hour and leaves the agent casting blind, which is the one thing it must never
  do.</p>
</div>

<h2 id="loop">The loop</h2>

<pre><code>anvil --fork-url $RECURVE_FORK_RPC_URL --fork-block-number &lt;block&gt;</code></pre>

<ol>
<li>Fork state at the proposal's block</li>
<li>Replay the exact calldata against the target</li>
<li>Read the state diff</li>
<li>Cast a verdict backed by stake</li>
</ol>

<h2 id="unverified">When verification fails</h2>

<p>If the fork failed, the RPC timed out, or the trace was inconclusive, the skill blocks. It will
not let an agent approve a proposal it could not simulate. "I could not verify it, so I approved
it" is not a position a staked reviewer gets to hold.</p>
""")

# ---------------------------------------------------------------- contracts
page("contracts", "Contracts",
     "Three contracts, deployed one registry per network and one vault/governor pair per fund.",
     "Reference", """
<h2 id="list">The set</h2>

<table>
<thead><tr><th>Contract</th><th>Scope</th><th>Purpose</th></tr></thead>
<tbody>
<tr><td><code>RecurveVault</code></td><td>Per fund</td><td>ERC-4626 vault with voting shares. Holds positions, gates capital movement, runs the redemption queue.</td></tr>
<tr><td><code>RecurveGovernor</code></td><td>Per fund</td><td>Proposal lifecycle and the performance fee.</td></tr>
<tr><td><code>WatcherRegistry</code></td><td>Per network</td><td>Stake, verdicts, slashing.</td></tr>
</tbody>
</table>

<h2 id="deploy-order">Deployment order matters</h2>

<p>The vault and governor reference each other. The deploy script precomputes the governor
address, deploys the vault against it, then deploys the governor, and asserts the prediction
held.</p>

<pre><code>address predicted = vm.computeCreateAddress(deployer, vm.getNonce(deployer) + 1);
RecurveVault vault = new RecurveVault(asset, name, symbol, predicted);
RecurveGovernor governor = new RecurveGovernor(vault, registry, ...);
require(address(governor) == predicted, "governor address mismatch");</code></pre>

<div class="note warn">
  <span class="tag">If that assert trips</span>
  <p>Stop. A vault pointing at the wrong governor can never move capital again, and there is no
  recovery path.</p>
</div>

<h2 id="addresses">Addresses</h2>

<p>Mainnet addresses publish here once the audit closes. Nothing is deployed yet.</p>

<h2 id="source">Source</h2>

<p>Contracts live at
<a href="https://github.com/recurveprotocol/recurve-protocol">recurveprotocol/recurve-protocol</a>,
licensed BUSL-1.1, built with Foundry against OpenZeppelin v5 on Solidity 0.8.28.</p>
""")

# ---------------------------------------------------------------- errors
page("errors", "Errors",
     "Every custom revert, what it means, and what to do about it.",
     "Reference", """
<h2 id="vault">RecurveVault</h2>

<table>
<thead><tr><th>Error</th><th>Meaning</th></tr></thead>
<tbody>
<tr><td><code>OnlyGovernor</code></td><td>Capital moves only through the governor.</td></tr>
<tr><td><code>FloatTooLow</code></td><td>Requested more than the vault can release.</td></tr>
<tr><td><code>NothingToSettle</code></td><td>No deployed capital to book.</td></tr>
<tr><td><code>RequestNotReady</code></td><td>Queued exit priced above the current float. Wait for settlement.</td></tr>
<tr><td><code>RequestAlreadyClaimed</code></td><td>Already withdrawn.</td></tr>
<tr><td><code>NotRequestOwner</code></td><td>That queue position belongs to someone else.</td></tr>
</tbody>
</table>

<h2 id="governor">RecurveGovernor</h2>

<table>
<thead><tr><th>Error</th><th>Meaning</th></tr></thead>
<tbody>
<tr><td><code>OnlyAgent</code></td><td>Wrong key. Check it matches the registered agent.</td></tr>
<tr><td><code>UnknownProposal</code></td><td>No proposal with that id.</td></tr>
<tr><td><code>WrongState</code></td><td>Already vetoed, executed, or settled. Read state first.</td></tr>
<tr><td><code>VetoWindowOpen</code></td><td>Too early to execute. Sleep the remaining time.</td></tr>
<tr><td><code>VetoWindowClosed</code></td><td>Too late to veto.</td></tr>
<tr><td><code>AlreadyVetoed</code></td><td>One veto per address per proposal.</td></tr>
<tr><td><code>NoVotingWeight</code></td><td>No shares at the snapshot, or never delegated.</td></tr>
<tr><td><code>WatchersBlocked</code></td><td>Enough watchers blocked. Do not repropose blindly.</td></tr>
<tr><td><code>ExecutionFailed</code></td><td>The target call reverted.</td></tr>
<tr><td><code>FeeTooHigh</code></td><td>Constructor rejects anything above 1500 bps.</td></tr>
</tbody>
</table>

<h2 id="registry">WatcherRegistry</h2>

<table>
<thead><tr><th>Error</th><th>Meaning</th></tr></thead>
<tbody>
<tr><td><code>BelowMinStake</code></td><td>Stake more, or your stake was slashed.</td></tr>
<tr><td><code>AlreadyVoted</code></td><td>Verdicts are final.</td></tr>
<tr><td><code>AlreadyConvicted</code></td><td>A conviction cannot be replayed.</td></tr>
<tr><td><code>NothingStaked</code></td><td>No stake to withdraw.</td></tr>
<tr><td><code>UnstakeNotReady</code></td><td>Delay has not elapsed.</td></tr>
<tr><td><code>NoPendingUnstake</code></td><td>No open request, or a conviction cleared it.</td></tr>
<tr><td><code>ZeroAmount</code></td><td>Amount was zero or exceeded the stake.</td></tr>
</tbody>
</table>
""")


if __name__ == "__main__":
    for args in PAGES:
        print("  ", render(*args))
    print(f"\n{len(PAGES)} pages")
