'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Bot, Sparkles, Send, Terminal, Sliders, Settings, Mic, Paperclip, 
  Cpu, Layers, Search, LogOut, Compass, FolderPlus, Clock, Pin, 
  Brain, Hammer, Award, CheckCircle2, ChevronRight, User, Trash2, 
  Play, RefreshCw, X, Shield, Plus, HelpCircle, Code, Palette, Wrench,
  Menu, Info, ThumbsUp, ThumbsDown, ChevronLeft, ArrowUp, CornerDownLeft
} from 'lucide-react';

// Color themes mapped to model keys with rich, premium hex color palettes
const MODEL_THEMES = {
  code: {
    primary: '#38bdf8', // sky-400
    accent: '#0284c7', // sky-600
    glow: 'rgba(56, 189, 248, 0.15)',
    bgGlow: 'from-sky-950/15 via-stone-950 to-stone-950',
    title: 'NEXA CODE',
    icon: '💻',
    tagline: 'Senior developer model optimized for high-performance syntax.'
  },
  design: {
    primary: '#ec4899', // pink-500
    accent: '#db2777', // pink-600
    glow: 'rgba(236, 72, 153, 0.15)',
    bgGlow: 'from-pink-950/15 via-stone-950 to-stone-950',
    title: 'NEXA DESIGN',
    icon: '🎨',
    tagline: 'UI/UX layout compiler mapped for symmetric visual styling.'
  },
  fix: {
    primary: '#ef4444', // red-500
    accent: '#dc2626', // red-600
    glow: 'rgba(239, 68, 68, 0.15)',
    bgGlow: 'from-red-950/15 via-stone-950 to-stone-950',
    title: 'NEXA FIX',
    icon: '🔧',
    tagline: 'Traceback debugger for runtime testing & structural repair.'
  },
  ultra: {
    primary: '#f59e0b', // amber-500
    accent: '#d97706', // amber-600
    glow: 'rgba(245, 158, 11, 0.15)',
    bgGlow: 'from-amber-950/15 via-stone-950 to-stone-950',
    title: 'NEXA ULTRA',
    icon: '✨',
    tagline: 'Master reasoning core coordinate and planner framework.'
  },
  god_eye: {
    primary: '#10b981', // emerald-500
    accent: '#059669', // emerald-600
    glow: 'rgba(16, 185, 129, 0.15)',
    bgGlow: 'from-emerald-950/15 via-stone-950 to-stone-950',
    title: 'NEXA GOD EYE',
    icon: '👁️',
    tagline: 'Agent supervisor orchestrating multiple background sub-processes.'
  }
};

const SLASH_COMMANDS = [
  { cmd: '/help', title: 'Help Suite', desc: 'Display all available slash commands', icon: HelpCircle },
  { cmd: '/model', title: 'Model Swapper', desc: 'Switch active AI specialized model', icon: Cpu, shortcut: '⚡' },
  { cmd: '/profile', title: 'Profile Manager', desc: 'View and edit memory traits', icon: User, shortcut: '👤' },
  { cmd: '/skill', title: 'Skill Registry', desc: 'Activate or remove modular tools', icon: Hammer, shortcut: '🛠️' },
  { cmd: '/stats', title: 'User Progress', desc: 'Check levels, XP progress, and streaks', icon: Award },
  { cmd: '/vault', title: 'Encrypted Vault', desc: 'Manage credentials and local secrets', icon: Shield },
  { cmd: '/insights', title: 'Weekly Reports', desc: 'Generate behavioral usage graphs', icon: Layers },
  { cmd: '/clear', title: 'Reset Context', desc: 'Clear active chat session history', icon: Trash2 },
  { cmd: '/challenges', title: 'Daily Challenge', desc: 'Load active model coding duel', icon: Compass }
];

// Quick Starter cards rendered on welcome screen
const STARTER_CARDS = [
  {
    icon: Code,
    label: 'Refactor Code',
    prompt: 'Optimize a FastAPI endpoint using an asynchronous SQLite connection cache.',
    color: 'text-sky-400'
  },
  {
    icon: Palette,
    label: 'Design Component',
    prompt: 'Create a dark-mode glassmorphic user profile card using vanilla CSS variables.',
    color: 'text-pink-400'
  },
  {
    icon: Wrench,
    label: 'Fix Traceback',
    prompt: 'Fix a Python subprocess execution timeout when invoking recursive shell commands.',
    color: 'text-red-400'
  },
  {
    icon: Sparkles,
    label: 'Orchestrate Tasks',
    prompt: 'Draft an architectural plan to deploy and schedule local sub-agents on cron timers.',
    color: 'text-emerald-400'
  }
];

// Monospace Code Block renderer with Clipboard interaction
const CodeBlock = ({ language, code }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="my-4 rounded-xl border border-stone-800/80 bg-[#0c0b0a] overflow-hidden shadow-lg font-mono">
      <div className="flex items-center justify-between px-4 py-2 bg-stone-900/60 border-b border-stone-900/80 text-[11px] text-stone-400 select-none">
        <span className="font-mono text-stone-400 font-semibold lowercase">{language || 'code'}</span>
        <button 
          onClick={handleCopy}
          className="flex items-center gap-1.5 hover:text-stone-200 transition-colors py-1 px-2 rounded hover:bg-stone-850 cursor-pointer"
        >
          {copied ? (
            <>
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
              <span className="text-emerald-500 font-medium font-sans">Copied</span>
            </>
          ) : (
            <>
              <Layers className="w-3.5 h-3.5" />
              <span className="font-sans">Copy code</span>
            </>
          )}
        </button>
      </div>
      <pre className="p-4 overflow-x-auto text-[12px] leading-relaxed text-stone-200 bg-transparent border-0 rounded-none m-0 scroll-clean">
        <code>{code.trim()}</code>
      </pre>
    </div>
  );
};

// Markdown message parser
const MessageFormatter = ({ text }) => {
  if (!text) return null;

  // Split content by code blocks
  const parts = text.split(/(```[\s\S]*?```)/g);

  return parts.map((part, idx) => {
    if (part.startsWith('```') && part.endsWith('```')) {
      const match = part.match(/```(\w*)\n([\s\S]*?)```/);
      const lang = match ? match[1] : 'code';
      const code = match ? match[2] : part.slice(3, -3);

      return <CodeBlock key={idx} language={lang} code={code} />;
    }

    // Process general prose styling
    return (
      <div key={idx} className="space-y-2 leading-relaxed">
        {part.split('\n').map((line, lIdx) => {
          // Preprocess bold notations from engine
          let currentText = line.replace(/\[bold\]/g, '**').replace(/\[\/bold\]/g, '**');
          
          let elements = [];
          const boldRegex = /\*\*(.*?)\*\*/g;
          let lastIndex = 0;
          let segmentId = 0;

          const boldMatches = [...currentText.matchAll(boldRegex)];
          if (boldMatches.length > 0) {
            boldMatches.forEach((m) => {
              const startIdx = m.index;
              const textBefore = currentText.slice(lastIndex, startIdx);
              const boldContent = m[1];
              
              if (textBefore) {
                // Check inline code within textBefore
                elements.push(...parseInlineCode(textBefore, segmentId++));
              }
              elements.push(<strong key={`bold-${segmentId++}`} className="font-semibold text-stone-100">{boldContent}</strong>);
              lastIndex = startIdx + m[0].length;
            });
            const textAfter = currentText.slice(lastIndex);
            if (textAfter) {
              elements.push(...parseInlineCode(textAfter, segmentId++));
            }
          } else {
            elements.push(...parseInlineCode(currentText, segmentId++));
          }

          // Helper for parsing inline code inside blocks
          function parseInlineCode(textSeg, baseId) {
            const inlineRegex = /`(.*?)`/g;
            const inlineMatches = [...textSeg.matchAll(inlineRegex)];
            if (inlineMatches.length === 0) return [<span key={`text-${baseId}`}>{textSeg}</span>];

            let segElements = [];
            let lastSegIndex = 0;
            let subId = 0;
            inlineMatches.forEach((m) => {
              const startSegIdx = m.index;
              const txtBefore = textSeg.slice(lastSegIndex, startSegIdx);
              const inlineCodeContent = m[1];

              if (txtBefore) {
                segElements.push(<span key={`txt-${baseId}-${subId++}`}>{txtBefore}</span>);
              }
              segElements.push(
                <code key={`code-${baseId}-${subId++}`} className="px-1.5 py-0.5 rounded bg-stone-900 border border-stone-850 text-stone-200 font-mono text-[11px] mx-0.5">
                  {inlineCodeContent}
                </code>
              );
              lastSegIndex = startSegIdx + m[0].length;
            });
            const txtAfter = textSeg.slice(lastSegIndex);
            if (txtAfter) {
              segElements.push(<span key={`txt-${baseId}-${subId++}`}>{txtAfter}</span>);
            }
            return segElements;
          }

          // Render list structures
          if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
            return (
              <li key={lIdx} className="ml-5 list-disc pl-1 text-stone-300 py-0.5">
                {elements}
              </li>
            );
          }
          if (line.trim().startsWith('• ')) {
            return (
              <li key={lIdx} className="ml-5 list-disc pl-1 text-stone-300 py-0.5">
                {elements}
              </li>
            );
          }
          if (/^\d+\.\s/.test(line.trim())) {
            return (
              <li key={lIdx} className="ml-5 list-decimal pl-1 text-stone-300 py-0.5">
                {elements}
              </li>
            );
          }

          // Section headings
          if (line.startsWith('### ')) {
            return <h4 key={lIdx} className="text-sm font-semibold text-stone-100 pt-3 pb-1">{line.replace('### ', '')}</h4>;
          }
          if (line.startsWith('## ')) {
            return <h3 key={lIdx} className="text-base font-semibold text-stone-100 pt-4 pb-1.5">{line.replace('## ', '')}</h3>;
          }
          if (line.startsWith('# ')) {
            return <h2 key={lIdx} className="text-lg font-bold text-stone-100 pt-5 pb-2">{line.replace('# ', '')}</h2>;
          }

          // Empty spaces
          if (line.trim() === '') {
            return <div key={lIdx} className="h-2" />;
          }

          return <p key={lIdx} className="text-stone-300 font-sans leading-relaxed">{elements}</p>;
        })}
      </div>
    );
  });
};

export default function NexaDashboard() {
  // Collapsible panel toggles
  const [leftSidebarOpen, setLeftSidebarOpen] = useState(true);
  const [rightSidebarOpen, setRightSidebarOpen] = useState(false);

  // Connection & model state
  const [activeModel, setActiveModel] = useState('ultra');
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'bot',
      text: "Neural link established. Welcome to NEXA Intelligence Operating System. I am ready to assist you. Type `/help` to see commands.",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      model: 'ultra'
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [latency, setLatency] = useState('0.000s');
  const [isOnline, setIsOnline] = useState(true);

  // Profile data sync
  const [userProfile, setUserProfile] = useState({
    name: 'Biruk',
    age: 25,
    interests: ['Coding', 'UI Design', 'AI Architecture'],
    mood: 'Methodical',
    chats: 142
  });

  // Action Skills
  const [skills, setSkills] = useState([
    { name: 'web_search', desc: 'Live Google & browser lookup', type: 'core' },
    { name: 'open_app', desc: 'Launch desktop applications', type: 'core' },
    { name: 'file_system', desc: 'Read, write, search local files', type: 'core' },
    { name: 'image_analysis', desc: 'Scan visuals and metadata', type: 'core' }
  ]);

  // Saved conversations
  const [recentChats, setRecentChats] = useState([
    { id: '1', title: 'Refactoring FastAPI server', pinned: true },
    { id: '2', title: 'Next.js 15 UI/UX Redesign', pinned: true },
    { id: '3', title: 'Local SQLite integration', pinned: false }
  ]);

  // Autocomplete commands menu
  const [showSlashMenu, setShowSlashMenu] = useState(false);
  const [slashSearch, setSlashSearch] = useState('');
  const [selectedSlashIndex, setSelectedSlashIndex] = useState(0);

  // References
  const chatEndRef = useRef(null);
  const textareaRef = useRef(null);
  const slashMenuRef = useRef(null);

  const theme = MODEL_THEMES[activeModel] || MODEL_THEMES.ultra;

  // Auto scroll chat list
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Autosize input textbox
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [inputText]);

  // Keyboard navigation inside slash command dropdown
  const handleKeyDown = (e) => {
    if (showSlashMenu) {
      const filtered = SLASH_COMMANDS.filter(c => 
        c.cmd.toLowerCase().includes(slashSearch.toLowerCase()) ||
        c.title.toLowerCase().includes(slashSearch.toLowerCase())
      );

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedSlashIndex(prev => (prev + 1) % Math.max(1, filtered.length));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedSlashIndex(prev => (prev - 1 + filtered.length) % Math.max(1, filtered.length));
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (filtered[selectedSlashIndex]) {
          applySlashCommand(filtered[selectedSlashIndex].cmd);
        }
      } else if (e.key === 'Escape') {
        e.preventDefault();
        setShowSlashMenu(false);
      }
    } else if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const applySlashCommand = (cmd) => {
    setInputText(cmd + ' ');
    setShowSlashMenu(false);
    textareaRef.current?.focus();
  };

  const handleInputChange = (e) => {
    const value = e.target.value;
    setInputText(value);

    if (value.startsWith('/')) {
      setShowSlashMenu(true);
      setSlashSearch(value);
      setSelectedSlashIndex(0);
    } else {
      setShowSlashMenu(false);
    }
  };

  // Sync state from FastAPI local server
  const fetchStatus = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/status');
      if (res.ok) {
        const data = await res.json();
        setIsOnline(true);
        if (data.active_model) {
          setActiveModel(data.active_model);
        }
        if (data.profile) {
          setUserProfile(data.profile);
        }
        if (data.skills) {
          setSkills(data.skills);
        }
      } else {
        setIsOnline(false);
      }
    } catch (e) {
      setIsOnline(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    // Poll connection status occasionally
    const interval = setInterval(fetchStatus, 8000);
    return () => clearInterval(interval);
  }, []);

  // Send input trigger
  const handleSend = async (customText = null) => {
    const text = (typeof customText === 'string' ? customText : inputText).trim();
    if (!text) return;

    setInputText('');
    setShowSlashMenu(false);

    // Render user message instantly
    const userMsg = {
      id: Date.now().toString(),
      sender: 'user',
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages(prev => [...prev, userMsg]);
    setIsTyping(true);

    // Client model toggle support
    if (text.startsWith('/model ')) {
      const targetModel = text.replace('/model ', '').trim().toLowerCase();
      if (MODEL_THEMES[targetModel]) {
        setActiveModel(targetModel);
      }
    }

    try {
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ message: text })
      });

      if (response.ok) {
        const data = await response.json();
        setLatency(data.latency || '0.045s');
        
        if (data.active_model) {
          setActiveModel(data.active_model);
        }
        
        setMessages(prev => [...prev, {
          id: (Date.now() + 1).toString(),
          sender: 'bot',
          text: data.response || '',
          timestamp: data.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          model: data.active_model || activeModel
        }]);

        if (text.startsWith('/profile') || text.startsWith('/skill') || text.includes('my name is') || text.includes('i am')) {
          fetchStatus();
        }
      } else {
        throw new Error('Offline link fallback');
      }
    } catch (err) {
      // Simulate backend routing offline
      setTimeout(() => {
        let simulatedReply = '';
        if (text.startsWith('/help')) {
          simulatedReply = "⚡ **NEXA Core Help Protocols**\n\nUse `/model [code|design|fix|ultra|god_eye]` to switch cognitive engines.\nUse `/profile` to list variables.\nUse `/clear` to clear active conversation history.";
        } else if (text.startsWith('/model')) {
          const parts = text.split(' ');
          if (parts[1] && MODEL_THEMES[parts[1].toLowerCase()]) {
            setActiveModel(parts[1].toLowerCase());
            simulatedReply = `Switched cognitive path to **${parts[1].toUpperCase()}** mode successfully.`;
          } else {
            simulatedReply = "Please specify an active model node: `code`, `design`, `fix`, `ultra`, or `god_eye`.";
          }
        } else if (text.startsWith('/profile')) {
          simulatedReply = `👤 **Offline Synaptic Profile**\n- **Name:** ${userProfile.name}\n- **Age:** ${userProfile.age} years\n- **Mood:** ${userProfile.mood}\n- **Interests:** ${userProfile.interests.join(', ')}`;
        } else if (text.startsWith('/clear')) {
          setMessages([]);
          simulatedReply = "Active chat buffer context has been cleared.";
        } else {
          simulatedReply = `Connection to local core backend on port 8000 is offline. Using simulated pipeline. Put real server online by running:\n\`\`\`bash\npython nexa_api.py\n\`\`\`\nInput received: "${text}"`;
        }

        setMessages(prev => [...prev, {
          id: (Date.now() + 1).toString(),
          sender: 'bot',
          text: simulatedReply,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          model: activeModel
        }]);
      }, 700);
    } finally {
      setIsTyping(false);
    }
  };

  const filteredSlashCommands = SLASH_COMMANDS.filter(c => 
    c.cmd.toLowerCase().includes(slashSearch.toLowerCase()) ||
    c.title.toLowerCase().includes(slashSearch.toLowerCase())
  );

  const hasWelcomeOnly = messages.length === 1 && messages[0].id === 'welcome';

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#0d0c0b] text-stone-100 font-sans selection:bg-stone-800 selection:text-amber-200">
      
      {/* Background cinematic aura matching the active model's custom theme colors */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden z-0">
        <div 
          className={`absolute -top-[35%] -left-[15%] w-[70%] h-[70%] rounded-full bg-gradient-to-br ${theme.bgGlow} filter blur-[130px] opacity-40 transition-all duration-700 ease-in-out`} 
          style={{ transform: 'translate3d(0, 0, 0)' }}
        />
        <div className="absolute -bottom-[20%] -right-[10%] w-[50%] h-[60%] rounded-full bg-stone-900/10 filter blur-[120px] opacity-20" />
      </div>

      {/* LEFT SIDEBAR (Collapsible Workspace Control Panel) */}
      <AnimatePresence initial={false}>
        {leftSidebarOpen && (
          <motion.aside 
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 280, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
            className="h-full flex flex-col border-r border-stone-900/80 bg-[#0e0d0c] select-none shrink-0 z-20 relative overflow-hidden"
          >
            {/* Header / Brand Logo */}
            <div className="p-5 flex items-center justify-between border-b border-stone-900/85 h-16 shrink-0">
              <div className="flex items-center gap-3">
                <div 
                  className="w-7 h-7 rounded-full flex items-center justify-center relative shadow-md transition-all duration-500"
                  style={{ 
                    backgroundImage: `radial-gradient(circle at 35% 35%, ${theme.primary}, ${theme.accent}, #1c1917)` 
                  }}
                >
                  <div className="absolute inset-0 rounded-full border border-white/10" />
                  <div className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
                </div>
                <div className="flex flex-col">
                  <span className="font-semibold text-xs tracking-wider text-stone-200">NEXA INTELLIGENCE</span>
                  <span className="text-[9px] text-stone-500 font-mono tracking-widest uppercase">CORE OS v4.0</span>
                </div>
              </div>
            </div>

            {/* Main sidebar content scroll box */}
            <div className="flex-1 overflow-y-auto scroll-clean p-4 space-y-6">
              
              {/* Workspace chat toggle */}
              <button 
                onClick={() => setMessages([{
                  id: 'welcome',
                  sender: 'bot',
                  text: "Workspace refreshed. Active core nodes online. Tell me what we should build today.",
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  model: activeModel
                }])}
                className="w-full flex items-center justify-center gap-2 py-2 px-4 rounded-lg bg-stone-900 hover:bg-stone-850 border border-stone-800/80 text-stone-300 hover:text-stone-100 transition-all text-xs font-medium cursor-pointer"
              >
                <FolderPlus className="w-4 h-4 text-stone-400" />
                New Workspace Chat
              </button>

              {/* Recent Active Channels */}
              <div>
                <div className="px-1.5 mb-2 flex items-center justify-between text-[10px] text-stone-500 font-mono uppercase tracking-wider">
                  <span>Channels</span>
                  <Pin className="w-3 h-3 text-stone-600" />
                </div>
                <div className="space-y-1">
                  {recentChats.map(c => (
                    <button 
                      key={c.id} 
                      className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg hover:bg-stone-900/60 hover:text-stone-300 text-left transition-colors text-xs group cursor-pointer"
                    >
                      <Clock className="w-3.5 h-3.5 text-stone-600 group-hover:text-stone-400" />
                      <span className="truncate flex-1">{c.title}</span>
                      {c.pinned && <Pin className="w-2.5 h-2.5 text-stone-650 rotate-45" />}
                    </button>
                  ))}
                </div>
              </div>

              {/* Memory Section */}
              <div className="space-y-2">
                <div className="px-1.5 flex items-center gap-1.5 text-[10px] text-stone-500 font-mono uppercase tracking-wider">
                  <Brain className="w-3 h-3 text-stone-500" />
                  <span>Synaptic Memory</span>
                </div>
                <div className="p-3 rounded-xl bg-stone-900/35 border border-stone-850/60 space-y-2">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="font-semibold text-stone-300">{userProfile.name}</span>
                    <span className="text-[9px] bg-stone-800 px-1.5 py-0.5 rounded text-stone-400 border border-stone-800 font-mono font-medium">{userProfile.mood}</span>
                  </div>
                  <div className="text-[10px] text-stone-500 space-y-1.5 font-sans leading-normal">
                    <div>Age: <span className="text-stone-400">{userProfile.age} yrs</span></div>
                    <div className="truncate">Interests: <span className="text-stone-400">{userProfile.interests.join(', ')}</span></div>
                    <div>Cognitive turns: <span className="text-stone-400">{userProfile.chats} loaded</span></div>
                  </div>
                </div>
              </div>

              {/* Core Skill Integrations */}
              <div>
                <div className="px-1.5 mb-2.5 flex items-center justify-between text-[10px] text-stone-500 font-mono uppercase tracking-wider">
                  <span>Engine Tools</span>
                  <Compass className="w-3 h-3 text-stone-600" />
                </div>
                <div className="space-y-1">
                  {skills.map(s => (
                    <div key={s.name} className="flex items-center justify-between px-2.5 py-1.5 rounded-lg bg-stone-900/15 hover:bg-stone-900/40 text-left transition-colors">
                      <div className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                        <span className="text-stone-300 font-mono text-[10px]">{s.name}</span>
                      </div>
                      <span className="text-[9px] text-stone-600 truncate max-w-[100px]">{s.desc}</span>
                    </div>
                  ))}
                </div>
              </div>

            </div>

            {/* Footer Profile Controls */}
            <div className="p-4 border-t border-stone-900/80 bg-[#0c0b0a] flex items-center justify-between shrink-0">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-stone-900 border border-stone-850 flex items-center justify-center font-bold text-stone-300 text-xs">
                  {userProfile.name[0] || 'U'}
                </div>
                <div className="flex flex-col">
                  <span className="font-semibold text-xs text-stone-300">{userProfile.name}</span>
                  <span className="text-[9px] text-stone-500">System Operator</span>
                </div>
              </div>
              <button className="p-2 rounded-lg hover:bg-stone-900 text-stone-500 hover:text-stone-300 transition-colors cursor-pointer">
                <Settings className="w-4 h-4" />
              </button>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* CENTRAL CHAT CONTAINER */}
      <main className="flex-1 flex flex-col z-10 relative overflow-hidden h-full">
        
        {/* Sleek Glass Header */}
        <header className="h-16 flex items-center justify-between px-6 border-b border-stone-900/60 bg-[#0e0d0c]/30 backdrop-blur-md shrink-0">
          <div className="flex items-center gap-3">
            {/* Sidebar toggle buttons */}
            <button 
              onClick={() => setLeftSidebarOpen(p => !p)} 
              className="p-1.5 rounded-lg hover:bg-stone-900/60 text-stone-400 hover:text-stone-200 transition-colors cursor-pointer"
              title="Toggle Left Sidebar"
            >
              {leftSidebarOpen ? <ChevronLeft className="w-4.5 h-4.5" /> : <Menu className="w-4.5 h-4.5" />}
            </button>

            {/* Status light indicators */}
            <div className="hidden sm:flex items-center gap-2 px-2 py-0.5 rounded-full border border-stone-900 bg-stone-950/40 text-[10px]">
              <span className={`w-1.5 h-1.5 rounded-full ${isOnline ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
              <span className="text-stone-400 font-mono">{isOnline ? 'Omni Link Active' : 'Offline'}</span>
            </div>
          </div>

          {/* Elegant Floating Model Swapper (Pill bar tabs) */}
          <div className="flex items-center gap-1 bg-[#151413] p-1 rounded-full border border-stone-900 shadow-sm max-w-sm sm:max-w-md select-none">
            {Object.keys(MODEL_THEMES).map((mKey) => {
              const active = mKey === activeModel;
              const details = MODEL_THEMES[mKey];
              return (
                <button
                  key={mKey}
                  onClick={() => {
                    setActiveModel(mKey);
                    // Also notify the backend engine of model swapper if online
                    handleSend(`/model ${mKey}`);
                  }}
                  className={`px-3 py-1 rounded-full text-[10px] font-mono tracking-wider font-semibold transition-all duration-300 flex items-center gap-1 cursor-pointer ${
                    active 
                      ? 'bg-stone-900 text-stone-100 border border-stone-850 shadow-inner' 
                      : 'text-stone-500 hover:text-stone-300'
                  }`}
                  title={details.tagline}
                >
                  <span className="scale-90">{details.icon}</span>
                  <span className="hidden md:inline text-[9px]">{mKey.toUpperCase()}</span>
                </button>
              );
            })}
          </div>

          {/* Right actions toggle inspector */}
          <div className="flex items-center gap-2">
            <span className="hidden sm:inline font-mono text-[10px] text-stone-500">Latency: {latency}</span>
            <button 
              onClick={() => setRightSidebarOpen(p => !p)} 
              className={`p-1.5 rounded-lg hover:bg-stone-900/60 text-stone-400 hover:text-stone-200 transition-all cursor-pointer ${rightSidebarOpen ? 'text-amber-500 bg-amber-500/10 border border-amber-500/10' : ''}`}
              title="Toggle System Inspector"
            >
              <Info className="w-4.5 h-4.5" />
            </button>
          </div>
        </header>

        {/* Workspace Chat Scroll Area */}
        <section className="flex-1 overflow-y-auto scroll-clean px-4 py-8 flex justify-center">
          <div className="w-full max-w-3xl flex flex-col space-y-8 pb-12">
            
            {/* Conditional Welcome Layout (Stunning Claude-like visual cards) */}
            {hasWelcomeOnly ? (
              <motion.div 
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.45 }}
                className="flex-1 flex flex-col justify-center items-center py-12 text-center"
              >
                {/* Core breathing logo icon */}
                <div 
                  className="w-16 h-16 rounded-3xl flex items-center justify-center animate-pulse-gentle shadow-2xl relative mb-6"
                  style={{ 
                    backgroundImage: `radial-gradient(circle at 35% 35%, ${theme.primary}, ${theme.accent}, #1c1917)` 
                  }}
                >
                  <div className="absolute inset-0 rounded-3xl border border-white/10" />
                  <Sparkles className="w-7 h-7 text-white" />
                </div>

                <h1 className="text-2xl font-semibold tracking-tight text-stone-200 max-w-md">
                  I am NEXA. How can I help you build today?
                </h1>
                <p className="text-xs text-stone-500 font-mono mt-2 mb-8 max-w-xs uppercase tracking-widest">
                  Neural active link • {theme.title}
                </p>

                {/* Grid Starter templates */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 w-full max-w-2xl text-left">
                  {STARTER_CARDS.map((card, index) => {
                    const CardIcon = card.icon;
                    return (
                      <motion.button
                        key={index}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 * index }}
                        onClick={() => {
                          setInputText(card.prompt);
                          textareaRef.current?.focus();
                        }}
                        className="p-4 rounded-xl border border-stone-900 bg-stone-950/60 hover:bg-stone-900/30 hover:border-stone-850 transition-all text-xs group text-left cursor-pointer shadow-sm hover:shadow-md relative overflow-hidden"
                      >
                        <div className="flex items-center gap-2.5 mb-1.5">
                          <CardIcon className={`w-4 h-4 ${card.color} group-hover:scale-105 transition-transform`} />
                          <span className="font-semibold text-stone-300 group-hover:text-stone-100 transition-colors">{card.label}</span>
                        </div>
                        <p className="text-stone-400 line-clamp-2 leading-relaxed text-[11px] group-hover:text-stone-300 transition-colors">
                          {card.prompt}
                        </p>
                      </motion.button>
                    );
                  })}
                </div>
              </motion.div>
            ) : (
              /* Normal Chat History list bubbles */
              <div className="space-y-6 flex-1">
                <AnimatePresence initial={false}>
                  {messages.map((m) => {
                    const isUser = m.sender === 'user';
                    const msgTheme = isUser ? null : (MODEL_THEMES[m.model] || MODEL_THEMES.ultra);
                    
                    return (
                      <motion.div 
                        key={m.id}
                        initial={{ opacity: 0, y: 12 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
                        className={`flex ${isUser ? 'justify-end' : 'justify-start'} w-full`}
                      >
                        <div className={`flex gap-4 max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
                          
                          {/* Round Avatar Icon */}
                          <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs shrink-0 select-none border border-stone-850/80 shadow-md ${
                            isUser 
                              ? 'bg-stone-900 text-stone-300 font-semibold' 
                              : 'bg-stone-950 text-stone-200'
                          }`}>
                            {isUser ? <User className="w-3.5 h-3.5" /> : <span>{msgTheme?.icon || '🤖'}</span>}
                          </div>

                          {/* Message Content Area */}
                          <div className="space-y-1">
                            <div className={`px-4 py-3 rounded-2xl text-[13px] leading-relaxed shadow-sm font-sans break-words border ${
                              isUser 
                                ? 'bg-[#1b1918] text-stone-100 rounded-tr-none border-stone-800 user-msg-shadow' 
                                : 'bg-[#0f0e0d] text-stone-200 rounded-tl-none border-stone-900/60 bot-msg-shadow'
                            }`}
                            style={isUser ? {} : {
                              borderLeft: `2.5px solid ${msgTheme?.primary || '#d97706'}`
                            }}
                            >
                              <MessageFormatter text={m.text} />
                            </div>

                            {/* Timestamp / Reaction items row */}
                            <div className={`flex items-center gap-2 px-1 py-0.5 text-[10px] text-stone-500 font-mono ${isUser ? 'justify-end' : 'justify-start'}`}>
                              <span>{m.timestamp}</span>
                              {!isUser && (
                                <>
                                  <span className="text-stone-700 select-none">•</span>
                                  <div className="flex gap-1.5">
                                    <button 
                                      className="p-1 rounded text-stone-600 hover:text-stone-400 hover:bg-stone-900 transition-colors cursor-pointer"
                                      title="Helpful response"
                                    >
                                      <ThumbsUp className="w-3 h-3" />
                                    </button>
                                    <button 
                                      className="p-1 rounded text-stone-600 hover:text-stone-400 hover:bg-stone-900 transition-colors cursor-pointer"
                                      title="Needs adjustments"
                                    >
                                      <ThumbsDown className="w-3 h-3" />
                                    </button>
                                    <button 
                                      onClick={() => navigator.clipboard.writeText(m.text)}
                                      className="p-1 rounded text-stone-600 hover:text-stone-400 hover:bg-stone-900 transition-colors cursor-pointer"
                                      title="Copy message contents"
                                    >
                                      <Layers className="w-3 h-3" />
                                    </button>
                                  </div>
                                </>
                              )}
                            </div>

                          </div>
                        </div>
                      </motion.div>
                    );
                  })}
                </AnimatePresence>
              </div>
            )}

            {/* Dynamic Loading Typing Dots */}
            {isTyping && (
              <motion.div 
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex justify-start w-full"
              >
                <div className="flex gap-4 flex-row">
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center bg-stone-950 border border-stone-900 text-xs shrink-0 select-none shadow-sm">
                    <span>{theme.icon}</span>
                  </div>
                  <div className="bg-[#0f0e0d] border border-stone-900/60 px-4 py-3.5 rounded-2xl rounded-tl-none flex items-center justify-center gap-1.5 h-[36px] w-[60px] bot-msg-shadow">
                    <div className="w-1.5 h-1.5 rounded-full bg-stone-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-1.5 h-1.5 rounded-full bg-stone-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-1.5 h-1.5 rounded-full bg-stone-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </motion.div>
            )}

            <div ref={chatEndRef} />
          </div>
        </section>

        {/* BOTTOM INPUT TEXTBOX BAR */}
        <section className="px-6 py-5 border-t border-stone-900/60 bg-[#0d0c0b]/40 backdrop-blur-xl shrink-0 z-30 relative">
          <div className="max-w-2xl mx-auto relative">
            
            {/* AUTOCOMPLETE protocalls console box */}
            <AnimatePresence>
              {showSlashMenu && filteredSlashCommands.length > 0 && (
                <motion.div 
                  ref={slashMenuRef}
                  initial={{ opacity: 0, y: 15, scale: 0.98 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.98 }}
                  transition={{ duration: 0.15, ease: 'easeOut' }}
                  className="absolute bottom-full left-0 right-0 mb-3.5 rounded-xl border border-stone-900 bg-stone-950/95 backdrop-blur-2xl shadow-2xl overflow-hidden max-h-64 flex flex-col z-50 text-xs select-none"
                >
                  <div className="p-2 border-b border-stone-900/80 bg-stone-950/60 text-[9px] text-stone-500 font-mono tracking-wider uppercase flex justify-between items-center select-none">
                    <span>NEXA SYSTEM CONSOLE PROTOCOLS</span>
                    <span>Navigate using ↑↓ arrows</span>
                  </div>
                  <div className="flex-1 overflow-y-auto py-1.5 scroll-clean">
                    {filteredSlashCommands.map((c, idx) => {
                      const IconComp = c.icon;
                      const isSelected = idx === selectedSlashIndex;
                      return (
                        <button
                          key={c.cmd}
                          onClick={() => applySlashCommand(c.cmd)}
                          className={`w-full flex items-center gap-3 px-3.5 py-2.5 text-left transition-all cursor-pointer ${
                            isSelected 
                              ? 'bg-stone-900 text-amber-500 font-medium border-l-2 border-amber-500 pl-[12px]' 
                              : 'text-stone-400 border-l-2 border-transparent hover:bg-stone-900/40 hover:text-stone-300'
                          }`}
                        >
                          <IconComp className={`w-4 h-4 shrink-0 ${isSelected ? 'text-amber-500' : 'text-stone-550'}`} />
                          <div className="flex-1 min-w-0 font-sans">
                            <span className="font-mono font-semibold block text-stone-250">{c.cmd}</span>
                            <span className="text-[10px] text-stone-500 truncate block mt-0.5">{c.desc}</span>
                          </div>
                          {c.shortcut && (
                            <span className="text-[9px] bg-stone-900 px-1.5 py-0.5 rounded border border-stone-850 font-mono text-stone-500">
                              {c.shortcut}
                            </span>
                          )}
                        </button>
                      );
                    })}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Custom Glowing Border Glass Input Area */}
            <div className="glass-input rounded-2xl flex flex-col p-2.5 shadow-md relative">
              <textarea
                ref={textareaRef}
                rows={1}
                value={inputText}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                placeholder="Ask NEXA anything or type '/' for core commands..."
                className="w-full bg-transparent border-0 ring-0 outline-none text-[13px] px-3.5 py-2.5 resize-none text-stone-100 placeholder-stone-500 leading-relaxed font-sans max-h-48 scroll-clean"
              />

              <div className="flex items-center justify-between border-t border-stone-900/50 pt-2 px-1">
                
                {/* Media Actions */}
                <div className="flex items-center gap-1">
                  <button className="p-2 rounded-lg hover:bg-stone-900/60 text-stone-500 hover:text-stone-300 transition-colors cursor-pointer" title="Upload file details">
                    <Paperclip className="w-4 h-4" />
                  </button>
                  <button className="p-2 rounded-lg hover:bg-stone-900/60 text-stone-500 hover:text-stone-300 transition-colors cursor-pointer" title="Neural dictation toggle">
                    <Mic className="w-4 h-4" />
                  </button>
                </div>

                {/* Interactive keys helper */}
                <div className="hidden sm:flex items-center gap-1 text-[9px] text-stone-600 font-mono select-none px-2 py-1 rounded bg-stone-950/20 border border-stone-900">
                  <span className="text-stone-500 font-semibold font-sans">Shift + Enter</span>
                  <span>new line</span>
                  <span className="text-stone-700 ml-1">|</span>
                  <CornerDownLeft className="w-2.5 h-2.5 ml-1 text-stone-600" />
                  <span>send</span>
                </div>

                {/* Custom active model color matched Submit button */}
                <button
                  onClick={() => handleSend()}
                  disabled={!inputText.trim()}
                  className="p-2 rounded-xl text-stone-950 transition-all font-semibold flex items-center justify-center cursor-pointer shadow-md disabled:opacity-40 disabled:pointer-events-none hover:scale-103"
                  style={{
                    backgroundColor: theme.primary,
                    color: '#0c0a09'
                  }}
                >
                  <ArrowUp className="w-4 h-4 stroke-[2.5]" />
                </button>
              </div>

            </div>
            
            <div className="text-[9px] text-stone-600 text-center mt-2.5 select-none font-mono tracking-wider">
              NEXA Professional Operating System Link Active • AES-256 Secured
            </div>

          </div>
        </section>

      </main>

      {/* RIGHT SIDEBAR - SYNAPTIC INSPECTOR (Collapsible telemetry analysis box) */}
      <AnimatePresence initial={false}>
        {rightSidebarOpen && (
          <motion.aside 
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 300, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
            className="h-full flex flex-col border-l border-stone-900/80 bg-[#0e0d0c] select-none shrink-0 z-20 overflow-hidden"
          >
            {/* Header Title */}
            <div className="p-5 flex items-center justify-between border-b border-stone-900/85 h-16 shrink-0">
              <span className="font-semibold text-xs tracking-wider text-stone-400 font-mono uppercase">Telemetry Metrics</span>
              <button 
                onClick={() => setRightSidebarOpen(false)}
                className="p-1 rounded hover:bg-stone-900 text-stone-500 hover:text-stone-300 transition-colors cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Scrollable details info */}
            <div className="flex-1 overflow-y-auto scroll-clean p-5 space-y-6">
              
              {/* Specialized AI Engine metadata card */}
              <div>
                <div className="text-[10px] text-stone-500 font-mono uppercase tracking-wider mb-2.5">Cognitive Core Spec</div>
                <div className="p-4 rounded-xl border border-stone-900 bg-stone-950/30 space-y-3 shadow-inner">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{theme.icon}</span>
                    <span className="font-semibold text-stone-200 text-xs font-mono">{theme.title}</span>
                  </div>
                  <p className="text-[10px] text-stone-400 leading-relaxed font-sans">
                    {theme.tagline}
                  </p>
                  <div className="h-px bg-stone-900" />
                  <div className="grid grid-cols-2 gap-2 text-[9px] font-mono text-stone-500">
                    <div>Temp: <span className="text-stone-300">{activeModel === 'code' ? '0.2' : activeModel === 'design' ? '0.7' : '0.5'}</span></div>
                    <div>Max context: <span className="text-stone-300">{activeModel === 'ultra' ? '8192' : '4096'}</span></div>
                  </div>
                </div>
              </div>

              {/* Performance load gauges */}
              <div>
                <div className="text-[10px] text-stone-500 font-mono uppercase tracking-wider mb-2.5">Engine Performance</div>
                <div className="space-y-4">
                  
                  {/* Response Speed Meter */}
                  <div className="space-y-1.5">
                    <div className="flex justify-between items-center text-[10px]">
                      <span className="text-stone-450">Active Turn Latency</span>
                      <span className="font-mono text-stone-250 font-semibold">{latency}</span>
                    </div>
                    <div className="w-full bg-stone-905 h-1 rounded-full overflow-hidden border border-stone-900/40">
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: latency === '0.000s' ? '0%' : '75%' }}
                        className="h-full rounded-full transition-all duration-500" 
                        style={{ 
                          backgroundColor: theme.primary 
                        }} 
                      />
                    </div>
                  </div>

                  {/* Fact Retrieval context memory load */}
                  <div className="space-y-1.5">
                    <div className="flex justify-between items-center text-[10px]">
                      <span className="text-stone-450">Synaptic Fact Load</span>
                      <span className="font-mono text-stone-250 font-semibold">12 / 100 Facts</span>
                    </div>
                    <div className="w-full bg-stone-905 h-1 rounded-full overflow-hidden border border-stone-900/40">
                      <div className="bg-stone-500 h-full rounded-full" style={{ width: '12%' }} />
                    </div>
                  </div>

                </div>
              </div>

              {/* User Gamification Stats Achievements section */}
              <div>
                <div className="text-[10px] text-stone-500 font-mono uppercase tracking-wider mb-2.5">Cognitive Milestones</div>
                <div className="space-y-2.5">
                  <div className="flex items-start gap-3 p-3 rounded-xl bg-stone-900/25 border border-stone-900/60">
                    <Award className="w-4.5 h-4.5 text-amber-500 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-semibold block text-stone-300 text-xs">Level 4 Scholar</span>
                      <span className="text-[9px] text-stone-500 block leading-normal mt-0.5">Unlocked engine models swapper console protocol</span>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 rounded-xl bg-stone-900/25 border border-stone-900/60">
                    <Award className="w-4.5 h-4.5 text-stone-400 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-semibold block text-stone-300 text-xs">First Integration</span>
                      <span className="text-[9px] text-stone-500 block leading-normal mt-0.5">Successfully executed local server API command</span>
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </motion.aside>
        )}
      </AnimatePresence>

    </div>
  );
}
