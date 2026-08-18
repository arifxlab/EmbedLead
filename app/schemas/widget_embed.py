from pydantic import BaseModel


class WidgetEmbedResponse(BaseModel):
    widget_id: str
    public_key: str
    embed_snippet: str
