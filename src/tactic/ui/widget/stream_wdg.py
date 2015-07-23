

__all__ = ["StreamWdg"]

from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer
from pyasm.widget import SelectWdg, WidgetConfig, IconWdg

from tactic.ui.common import BaseRefreshWdg


class StreamWdg(BaseRefreshWdg):

    def get_display(my):
        return "
            <main>
        <div id="welcome">
            <h1 class="title med-font">Check the tweet temperature of:</h1>
            <form class="form-inline">
                <div class="form-group">
                    <input type="topic" class="form-control" id="topic" placeholder="UofTHacks" value="UofTHacks">
                    <a href="#load-overlay">
                        <button type="submit" class="btn btn-default" id="search"><i class="fa fa-eyedropper"></i></button>
                    </a>
                </div>
            </form>
            
        </div>

        <div id="load-overlay">
            <h1 class="title big-font">This conversation's getting heated...</h1>
        </div>

        <a href="#welcome">
            <div id="back-top">
                <i class="fa fa-arrow-circle-up fa-5x"></i>
            </div>
        </a>
        <div id="map-canvas"></div>
    </main>"
