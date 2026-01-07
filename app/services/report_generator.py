from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from datetime import datetime
from pathlib import Path

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


# For Basic Pie chart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.piecharts import Pie
from reportlab.pdfbase.pdfmetrics import stringWidth, EmbeddedType1Face, registerTypeFace, Font, registerFont
from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin
from reportlab.lib.colors import Color, PCMYKColor, white

#emotion_tally = [0, 0, 0]
#n_user_messages = 0


def generate_report_pdf(conversation: dict, output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph(
        f"<b>{conversation.get('title', 'Conversation Report')}</b>",
        styles["Title"],
    ))
    story.append(Spacer(1, 12))

    # Metadata
    story.append(Paragraph(
        f"<b>Conversation ID:</b> {conversation['conversation_id']}",
        styles["Normal"],
    ))

    created_at = conversation.get("created_at")
    updated_at = conversation.get("updated_at")

    if created_at:
        story.append(Paragraph(
            f"<b>Created:</b> {created_at.strftime('%Y-%m-%d %H:%M:%S')} GMT",
            styles["Normal"],
        ))

    if updated_at:
        story.append(Paragraph(
            f"<b>Last updated:</b> {updated_at.strftime('%Y-%m-%d %H:%M:%S')} GMT",
            styles["Normal"],
        ))

    story.append(Spacer(1, 20))

    # Messages (Q&A)
    messages = conversation["messages"]

    # Emotion overall count
    emotion_count = 0
    emotion_tally = [0, 0, 0]
    # emotion_emojis = ["😊", "😐", "😟", "🤖"]  # [happy, neutral, sad, robot]
    emotion_emojis = [":)", ":|", ":("]
    emoji = emotion_emojis[0]
    emotion_flag = False # check if there are any emotions saved

    n_user_messages = len(messages)/ 2
    
    for i in range(0, len(messages), 2):
        user_msg = messages[i]
        assistant_msg = messages[i + 1] if i + 1 < len(messages) else None

        user_emotion = user_msg.get("emotion")

        if user_emotion:
            emotion_flag = True
            if user_emotion == "positive":
                emotion_count += 1
                emotion_tally[0] += 1
                emoji = emotion_emojis[0]
            elif user_emotion == "neutral":
                emotion_count += 0
                emotion_tally[1] += 1
                emoji = emotion_emojis[1]
            else:
                emotion_count -= 1
                emotion_tally[2] += 1
                emoji = emotion_emojis[2]


        story.append(Paragraph(
            f"<b>You:</b> {user_msg['content']} [<b>{emoji}</b>]",
            styles["Normal"],
        ))
        story.append(Spacer(1, 6))

        if assistant_msg:
            story.append(Paragraph(
                f"<b>AI:</b> {assistant_msg['content']}",
                styles["Normal"],
            ))

        story.append(Spacer(1, 14))


    story.append(Spacer(1, 6))
    
    # Sentiment summary
    if emotion_count > 1:
        story.append(Paragraph(
            f"<b>Sentiment summary:</b> The conversation maintained a generally positive tone, indicating engagement and confidence.",
            styles["Normal"],
        ))
    elif emotion_count < -1:
        story.append(Paragraph(
            f"<b>Sentiment summary:</b> The conversation maintained a generally negative tone, indicating signs of frustration and lack of engagement.",
            styles["Normal"],
        ))
    else:
        story.append(Paragraph(
            f"<b>Sentiment summary:</b> The conversation remained mostly neutral and balanced, neither overly positive nor negative.",
            styles["Normal"],
        ))

    story.append(Spacer(1, 2))

    if emotion_flag:
        story.append(PieChart02(emotion_tally, n_user_messages))


    doc.build(story)


# https://www.reportlab.com/chartgallery/pie/PieChart02/?iframe=true&width=900&height=500&ajax=true 
class PieChart02(_DrawingEditorMixin, Drawing):
    '''
        A Pie Chart
        ===========

        This is a simple pie chart that contains a basic legend.
    '''
    def __init__(self,emotion_tally, n_user_messages,width=400,height=200,*args,**kw):
        Drawing.__init__(self,width,height,*args,**kw)
        fontSize    = 8
        fontName    = 'Helvetica'
        #title
        # self.titleText = "User sentiment"
        #pie
        self._add(self,Pie(),name='pie',validate=None,desc=None)
        self.pie.strokeWidth            = 1
        self.pie.slices.strokeColor     = PCMYKColor(0,0,0,0)
        self.pie.slices.strokeWidth     = 1
        #legend
        self._add(self,Legend(),name='legend',validate=None,desc=None)
        self.legend.columnMaximum       = 99
        self.legend.alignment='right'
        self.legend.dx                  = 6
        self.legend.dy                  = 6
        self.legend.dxTextSpace         = 5
        self.legend.deltay              = 10
        self.legend.strokeWidth         = 0
        self.legend.subCols[0].minWidth = 75
        self.legend.subCols[0].align = 'left'
        self.legend.subCols[1].minWidth = 25
        self.legend.subCols[1].align = 'right'
        self.pie.data = [x * 100/n_user_messages for x in emotion_tally]
        self.height      = 200
        self.legend.boxAnchor           = 'c'
        self.legend.y                   = 100
        colors = {
            "green":      PCMYKColor(100,0,90,50,alpha=100),
            "blue":       PCMYKColor(100,60,0,50,alpha=100),
            "red":        PCMYKColor(0,100,100,40,alpha=100),
            "light blue": PCMYKColor(66,13,0,22,alpha=100),
            "white":      PCMYKColor(0,0,0,0,alpha=100)
        }
        self.pie.strokeColor            = colors["white"]
        self.pie.slices[0].fillColor    = colors["green"]
        self.pie.slices[1].fillColor    = colors["blue"]
        self.pie.slices[2].fillColor    = colors["red"]
        # self.pie.slices[3].fillColor  = colors["light blue"]
        self.legend.colorNamePairs = [
            (colors["green"], ('Positive', '{0:.1f}%'.format(self.pie.data[0]))),
            (colors["blue"], ('Neutral',  '{0:.1f}%'.format(self.pie.data[1]))),
            (colors["red"], ('Negative', '{0:.1f}%'.format(self.pie.data[2]))),
        ]
        self.width                = 400
        self.legend.x             = 350
        self.pie.width            = 150
        self.pie.height           = 150
        self.pie.y                = 25
        self.pie.x                = 25


