from sqlalchemy.orm import Session
from chat.tables import ChatTable
from chat.chat_summaries.tables import ChatSummaryTable
import uuid

def set_agent_chat_summary_in_db(db: Session, chat_id: uuid.UUID, agent_name: str, content: str):
    chat = db.get(ChatTable, chat_id)
    assert chat
    
    # Look for the summary for the given chat and agent.
    summary = db.query(ChatSummaryTable).filter(ChatSummaryTable.chat_id == chat_id, ChatSummaryTable.agent_name == agent_name).first()

    if summary is None:
        # Create a summary with the given content if it didn't exist.
        summary = ChatSummaryTable(
            chat_id=chat_id,
            agent_name=agent_name,
            content=content,
        )
        db.add(summary)
    else:
        # Change the summary's content.
        summary.content = content

    db.commit()
    