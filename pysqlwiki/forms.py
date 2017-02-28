import colander
import deform.widget


class PageForm(colander.MappingSchema):
    name = colander.SchemaNode(
        colander.String()
    )

    body = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.RichTextWidget()
    )
