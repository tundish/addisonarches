// This file is part of turberfield.
//
// Turberfield is free software: you can redistribute it and/or modify it
// under the terms of the GNU General Public License as published
// by the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Turberfield is distributed in the hope that it will be useful, but
// WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with turberfield.  If not, see <http://www.gnu.org/licenses/>.


function get_loop(name) {
    var audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    var source = audioCtx.createBufferSource();
    var request = new XMLHttpRequest();

    request.open("GET", "/audio/" + name, true);

    request.responseType = "arraybuffer";

    request.onload = function() {
        var audioData = request.response;

        audioCtx.decodeAudioData(audioData, function(buffer) {
            var myBuffer = buffer;
            source.buffer = myBuffer;
            source.connect(audioCtx.destination);
            source.loop = true;
          },

          function(e){"Error with decoding audio data" + e.err});

    }

    request.send();
    return source; 
}
