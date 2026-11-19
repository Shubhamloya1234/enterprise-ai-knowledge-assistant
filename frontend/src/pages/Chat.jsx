import {
    useCallback,
    useEffect,
    useRef,
    useState,
} from "react";
import api from "../services/api";
import Sidebar from "../components/Sidebar";

function Chat() {
    const [conversations, setConversations] = useState([]);
    const [activeConversation, setActiveConversation] = useState(null);
    const [messages, setMessages] = useState([]);
    const [question, setQuestion] = useState("");
    const [loading, setLoading] = useState(false);
    const [loadingConversations, setLoadingConversations] = useState(true);

    const messagesEndRef = useRef(null);

    // Auto-scroll
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({
            behavior: "smooth",
        });
    }, [messages, loading]); 

    // Load conversations
    const loadConversations = useCallback(async () => {
    try {
        const response = await api.get("/conversations/");
        const data = response.data;

        setConversations(data);

        setActiveConversation((current) => {
            if (
                current === null &&
                data.length > 0
            ) {
                return data[0].id;
            }

            return current;
        });
    } catch (error) {
        console.error(
            "Failed to load conversations:",
            error
        );
    } finally {
        setLoadingConversations(false);
    }
}, []);

    // Load messages
    const loadConversation = useCallback(async (conversationId) => {
    try {
        const response = await api.get(
            `/conversations/${conversationId}`
        );

        const loadedMessages = response.data.messages || [];

        setMessages(
            loadedMessages.map((message) => ({
                ...message,
                timestamp: message.timestamp || new Date(),
            }))
        );
    } catch (error) {
        console.error(
            "Failed to load conversation:",
            error
        );
    }
}, []);

    // Initial conversation loading.
useEffect(() => {
    const timeoutId = setTimeout(() => {
        loadConversations();
    }, 0);

    return () => clearTimeout(timeoutId);
}, [loadConversations]);

// Load messages when the selected conversation changes.
useEffect(() => {
    if (activeConversation === null) {
        return;
    }

    const timeoutId = setTimeout(() => {
        loadConversation(activeConversation);
    }, 0);

    return () => clearTimeout(timeoutId);
}, [activeConversation, loadConversation]);

    // Create conversation
    const createConversation = async () => {
        try {
            const response = await api.post(
                "/conversations/",
                {
                    title: null,
                }
            );

            const newConversation = response.data;

            setConversations((previous) => [
                newConversation,
                ...previous,
            ]);

            setActiveConversation(newConversation.id);
            setMessages([]);

        } catch (error) {
            console.error(
                "Failed to create conversation:",
                error
            );
        }
    };

    // Send message
    const sendMessage = async (event) => {
        event.preventDefault();

        if (
            !question.trim() ||
            activeConversation === null ||
            loading
        ) {
            return;
        }

        const currentQuestion = question.trim();

        setQuestion("");

        // Show user message immediately
     

        setLoading(true);

        try {
            const response = await api.post(
                "/agent/ask",
                {
                    question: currentQuestion,
                    conversation_id: activeConversation,
                }
            );

            console.log("FULL API RESPONSE:", response.data);
console.log("RAG TOOL RESULT:", response.data.tool_result);
console.log("RAG SOURCES:", response.data.tool_result?.sources);

            if (conversations.find(
    (conversation) =>
        conversation.id === activeConversation
)?.title === null) {

    setConversations((previous) =>
        previous.map((conversation) =>
            conversation.id === activeConversation
                ? {
                    ...conversation,
                    title: currentQuestion.slice(0, 50),
                }
                : conversation
        )
    );
}

            // Show assistant response
setMessages((previous) => [
    ...previous,
    {
        id: `temp-assistant-${Date.now()}`,
        role: "assistant",
        content: response.data.answer,
        sources: response.data.tool_result?.sources || [],
        timestamp: new Date(),
    },
]);
            await loadConversations();

        } catch (error) {
            console.error(
                "Failed to send message:",
                error
            );

            setMessages((previous) => [
                ...previous,
                {
                    id: `error-${Date.now()}`,
                    role: "assistant",
                    content:
                        "Unable to get a response from the server.",
                    timestamp: new Date(),
                },
            ]);

        } finally {
            setLoading(false);
        }
    };

    // Format time
    const formatTime = (timestamp) => {
        if (!timestamp) {
            return "";
        }

        return new Date(timestamp).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
        });
    };

    if (loadingConversations) {
        return (
            <div className="loading-screen">
                Loading conversations...
            </div>
        );
    }

    const deleteConversation = async (conversationId) => {
    const confirmed = window.confirm(
        "Are you sure you want to delete this conversation?"
    );

    if (!confirmed) {
        return;
    }

    try {
        await api.delete(
            `/conversations/${conversationId}`
        );

        setConversations((previous) =>
            previous.filter(
                (conversation) =>
                    conversation.id !== conversationId
            )
        );

        if (activeConversation === conversationId) {
            setActiveConversation(null);
            setMessages([]);
        }

    } catch (error) {
        console.error(
            "Failed to delete conversation:",
            error
        );
    }
};

    return (
        <div className="app-layout">

            <Sidebar
    conversations={conversations}
    activeConversation={activeConversation}
    onSelectConversation={setActiveConversation}
    onNewConversation={createConversation}
    onDeleteConversation={deleteConversation}
/>

            <main className="chat-page">

                <header className="chat-header">
                    <h1>AI Enterprise Assistant</h1>
                    <p>
                        Ask questions about your company
                    </p>
                </header>

                <div className="chat-container">

                    <div className="messages">

                        {activeConversation === null && (
                            <div className="welcome">
                                <h2>
                                    Start a new conversation
                                </h2>

                                <p>
                                    Click "+ New Chat" to begin.
                                </p>
                            </div>
                        )}

                        {activeConversation !== null &&
                            messages.length === 0 && (
                                <div className="welcome">

                                    <h2>
                                        How can I help you?
                                    </h2>

                                    <p>
                                        Ask about company
                                        policies, employees,
                                        or calculations.
                                    </p>

                                </div>
                            )}
                        
                        console.log("ASSISTANT MESSAGE SOURCES:",response.data.tool_result?.sources);

                        {messages.map((message) => (
                            <div
                                key={message.id}
                                className={`message ${message.role}`}
                            >

                                <div className="message-wrapper">
<div className="message-content">
    {message.content}
</div>

{message.role === "assistant" &&
    message.sources?.length > 0 && (
        <div className="message-sources">
            <strong>Sources</strong>

            {message.sources.map((source, index) => (
                <div
                    className="message-source"
                    key={`${source.source}-${source.chunk_index}-${index}`}
                >
                    <span>📄 {source.source}</span>
                    <small>Chunk {source.chunk_index}</small>
                </div>
            ))}
        </div>
    )}

<div className="message-time">
    {formatTime(message.timestamp)}
</div>

                                </div>

                            </div>
                        ))}

                        {loading && (
                            <div className="message assistant">

                                <div className="message-wrapper">

                                    <div className="thinking">
                                        <span></span>
                                        <span></span>
                                        <span></span>
                                    </div>

                                </div>

                            </div>
                        )}

                        <div ref={messagesEndRef} />

                    </div>

                    <form
                        className="chat-input"
                        onSubmit={sendMessage}
                    >

                        <textarea
    value={question}
    onChange={(event) =>
        setQuestion(event.target.value)
    }
    onKeyDown={(event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();

            if (
                question.trim() &&
                activeConversation !== null &&
                !loading
            ) {
                event.currentTarget.form.requestSubmit();
            }
        }
    }}
    placeholder={
        activeConversation === null
            ? "Create a conversation first..."
            : "Ask something..."
    }
    disabled={
        loading ||
        activeConversation === null
    }
/>

                        <button
                            type="submit"
                            disabled={
                                loading ||
                                activeConversation === null ||
                                !question.trim()
                            }
                        >
                            {loading ? "Thinking..." : "Send"}
                        </button>

                    </form>

                </div>

            </main>

        </div>
    );
}

export default Chat;