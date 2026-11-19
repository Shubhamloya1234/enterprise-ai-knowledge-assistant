import { useAuth } from "../context/auth";
import { Link } from "react-router-dom";

function Sidebar({
    conversations,
    activeConversation,
    onSelectConversation,
    onNewConversation,
    onDeleteConversation,
}) {

    const { logout, user } = useAuth();

    return (
        <aside className="sidebar">

            <div className="sidebar-header">

                <h2>
                    AI Assistant
                </h2>

                <button
                    className="new-chat-button"
                    onClick={onNewConversation}
                >
                    + New Chat
                </button>

                {user?.role === "ADMIN" && (
    <Link
        to="/documents"
        className="sidebar-nav-link"
    >
        Document Management
    </Link>
)}

            </div>


            <div className="conversation-list">

                {conversations.length === 0 && (
                    <p className="empty-conversations">
                        No conversations yet
                    </p>
                )}

                {conversations.map((conversation) => (
    <div
        key={conversation.id}
        className={`conversation-item ${
            activeConversation === conversation.id
                ? "active"
                : ""
        }`}
    >
        <button
            className="conversation-select"
            onClick={() =>
                onSelectConversation(conversation.id)
            }
        >
            {conversation.title || "New Conversation"}
        </button>

        <button
            className="conversation-delete"
            onClick={(event) => {
                event.stopPropagation();
                onDeleteConversation(conversation.id);
            }}
        >
            ×
        </button>
    </div>
))}

            </div>


            <div className="sidebar-footer">

                <div className="user-info">

                    <div className="user-avatar">
    {user?.role?.charAt(0) || "U"}
</div>

<div className="user-details">

    <strong>
        {user?.username || `User ${user?.user_id || ""}`}
    </strong>

    <span>
        {user?.role || "USER"}
    </span>

</div>

                </div>


                <button
                    className="logout-button"
                    onClick={logout}
                >
                    Logout
                </button>

            </div>

        </aside>
    );
}

export default Sidebar;