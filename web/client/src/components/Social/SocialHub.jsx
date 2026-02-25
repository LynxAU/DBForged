import React, { useState } from 'react'

/**
 * SocialHub - Friends, Guild, Mail
 */
export function SocialHub({ player, onCommand }) {
  const [activeTab, setActiveTab] = useState('friends')

  // Mock data - would come from server
  const friends = [
    { name: 'Goku', status: 'online', location: 'North City' },
    { name: 'Vegeta', status: 'online', location: 'Capsule Corp' },
    { name: 'Piccolo', status: 'away', location: 'Mount Paozu' },
    { name: 'Krillin', status: 'offline', location: 'West City' },
  ]

  const guild = {
    name: 'Z-Fighters',
    rank: 'Leader',
    members: [
      { name: 'Goku', rank: 'Leader', online: true, pl: 1500000 },
      { name: 'Vegeta', rank: 'Officer', online: true, pl: 1400000 },
      { name: 'Piccolo', rank: 'Member', online: true, pl: 800000 },
      { name: 'Gohan', rank: 'Member', online: false, pl: 600000 },
    ],
    motd: 'Training for the next threat!',
    bank: 50000,
  }

  const mail = [
    { from: 'King Cold', subject: 'Greeting', unread: true, time: '2h ago' },
    { from: 'Frieza', subject: 'Business Proposal', unread: true, time: '1d ago' },
    { from: 'Bulma', subject: 'New Equipment', unread: false, time: '3d ago' },
  ]

  const tabs = [
    { id: 'friends', label: 'Friends', icon: '👥' },
    { id: 'guild', label: 'Guild', icon: '⚔️' },
    { id: 'mail', label: 'Mail', icon: '📧', unread: 2 },
  ]

  return (
    <div className="social-hub">
      {/* Tab Bar */}
      <div className="social-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`social-tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
            {tab.unread && <span className="unread-badge">{tab.unread}</span>}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="social-content">
        {activeTab === 'friends' && (
          <div className="friends-panel">
            <div className="section-header">
              <span>Friends List</span>
              <button onClick={() => onCommand('friend add ')}>+ Add</button>
            </div>
            
            {friends.map((friend, i) => (
              <div key={i} className="friend-row">
                <div className="friend-status">
                  <span className={`status-dot ${friend.status}`} />
                  <span className="friend-name">{friend.name}</span>
                </div>
                <div className="friend-info">
                  <span className="friend-location">{friend.location}</span>
                  <span className={`status-label ${friend.status}`}>{friend.status}</span>
                </div>
                <div className="friend-actions">
                  <button onClick={() => onCommand(`tell ${friend.name} `)}>Tell</button>
                  <button onClick={() => onCommand(`visit ${friend.name}`)}>Visit</button>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'guild' && (
          <div className="guild-panel">
            {/* Guild Header */}
            <div className="guild-header">
              <div className="guild-emblem">⚔️</div>
              <div className="guild-info">
                <h3>{guild.name}</h3>
                <span>Your Rank: {guild.rank}</span>
              </div>
            </div>

            {/* MOTD */}
            <div className="guild-motd">
              <span className="motd-label">Message of the Day:</span>
              <p>{guild.motd}</p>
            </div>

            {/* Bank */}
            <div className="guild-bank">
              <span>🏦 Guild Bank:</span>
              <span className="zeni">{guild.bank.toLocaleString()} zeni</span>
            </div>

            {/* Members */}
            <div className="guild-members">
              <span className="section-title">Members ({guild.members.length})</span>
              {guild.members.map((member, i) => (
                <div key={i} className="member-row">
                  <span className={`status-dot ${member.online ? 'online' : 'offline'}`} />
                  <span className="member-name">{member.name}</span>
                  <span className="member-rank">{member.rank}</span>
                  <span className="member-pl">{member.pl.toLocaleString()} PL</span>
                </div>
              ))}
            </div>

            {/* Actions */}
            <div className="guild-actions">
              <button onClick={() => onCommand('guild motd ')}>Set MOTD</button>
              <button onClick={() => onCommand('guild invite ')}>Invite</button>
              <button onClick={() => onCommand('guild leave ')}>Leave</button>
            </div>
          </div>
        )}

        {activeTab === 'mail' && (
          <div className="mail-panel">
            <div className="section-header">
              <span>Inbox</span>
              <button onClick={() => onCommand('mail compose ')}>+ Compose</button>
            </div>

            {mail.map((msg, i) => (
              <div key={i} className={`mail-row ${msg.unread ? 'unread' : ''}`}>
                <div className="mail-sender">{msg.from}</div>
                <div className="mail-subject">{msg.subject}</div>
                <div className="mail-time">{msg.time}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      <style>{`
        .social-hub {
          display: flex;
          flex-direction: column;
          height: 100%;
        }

        .social-tabs {
          display: flex;
          border-bottom: 1px solid rgba(0, 174, 255, 0.2);
        }

        .social-tab {
          flex: 1;
          padding: 12px;
          background: transparent;
          border: none;
          color: #888;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          position: relative;
        }

        .social-tab.active {
          color: #00aeff;
          background: rgba(0, 174, 255, 0.1);
        }

        .unread-badge {
          position: absolute;
          top: 4px;
          right: 20%;
          background: #ff3366;
          color: #fff;
          font-size: 0.7rem;
          padding: 2px 6px;
          border-radius: 10px;
        }

        .social-content {
          flex: 1;
          overflow: auto;
          padding: 16px;
        }

        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .section-header button {
          padding: 6px 12px;
          background: #00aeff;
          border: none;
          border-radius: 4px;
          color: #000;
          font-weight: 600;
          cursor: pointer;
        }

        .friend-row, .member-row, .mail-row {
          display: flex;
          align-items: center;
          padding: 12px;
          background: rgba(0, 0, 0, 0.3);
          border-radius: 8px;
          margin-bottom: 8px;
        }

        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          margin-right: 8px;
        }

        .status-dot.online { background: #32ff64; }
        .status-dot.away { background: #ffd74a; }
        .status-dot.offline { background: #666; }

        .friend-name, .member-name {
          font-weight: 600;
          flex: 1;
        }

        .friend-location, .member-rank {
          font-size: 0.85rem;
          opacity: 0.7;
          margin-right: 12px;
        }

        .status-label.online { color: #32ff64; }
        .status-label.away { color: #ffd74a; }
        .status-label.offline { color: #666; }

        .friend-actions {
          display: flex;
          gap: 4px;
        }

        .friend-actions button {
          padding: 4px 8px;
          background: rgba(0, 174, 255, 0.2);
          border: 1px solid #00aeff;
          border-radius: 4px;
          color: #00aeff;
          font-size: 0.8rem;
          cursor: pointer;
        }

        .guild-header {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 16px;
        }

        .guild-emblem {
          font-size: 2.5rem;
        }

        .guild-info h3 {
          margin: 0;
          color: #ff6b35;
        }

        .guild-motd {
          background: rgba(255, 107, 53, 0.1);
          border: 1px solid rgba(255, 107, 53, 0.3);
          border-radius: 8px;
          padding: 12px;
          margin-bottom: 16px;
        }

        .motd-label {
          font-size: 0.8rem;
          color: #ff6b35;
        }

        .guild-motd p {
          margin: 8px 0 0;
        }

        .guild-bank {
          display: flex;
          justify-content: space-between;
          padding: 12px;
          background: rgba(0, 0, 0, 0.3);
          border-radius: 8px;
          margin-bottom: 16px;
        }

        .zeni {
          color: #ffd74a;
          font-weight: 600;
        }

        .section-title {
          display: block;
          margin-bottom: 8px;
          font-weight: 600;
        }

        .member-pl {
          font-size: 0.85rem;
          color: #00aeff;
        }

        .guild-actions {
          display: flex;
          gap: 8px;
          margin-top: 16px;
        }

        .guild-actions button {
          flex: 1;
          padding: 8px;
          background: rgba(255, 107, 53, 0.2);
          border: 1px solid #ff6b35;
          border-radius: 6px;
          color: #ff6b35;
          cursor: pointer;
        }

        .mail-row.unread {
          background: rgba(0, 174, 255, 0.1);
          border-left: 3px solid #00aeff;
        }

        .mail-sender {
          font-weight: 600;
          width: 100px;
        }

        .mail-subject {
          flex: 1;
        }

        .mail-time {
          font-size: 0.8rem;
          opacity: 0.5;
        }
      `}</style>
    </div>
  )
}

export default SocialHub
