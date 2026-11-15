#include <glad/gl.h>
#define GLFW_INCLUDE_NONE
#include <GLFW/glfw3.h>
#include "Shader.hpp"
#include "HDRFramebuffer.hpp"
#include "BloomEffect.hpp"
#include "RenderOptions.hpp"
#include "PngWriter.hpp"
#include "UniverseCamera.hpp"
#include "GalaxyCatalog.hpp"
#include <glm/gtc/type_ptr.hpp>
#include <algorithm>
#include <chrono>
#include <cstdio>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

void framebufferSizeCallback(GLFWwindow*,int w,int h) { glViewport(0,0,w,h); }

// STAGES 2/3/5: world-space ray camera, view basis and perspective projection.
// The original pre-45s math and shader bytes are deliberately preserved.
void drawVolume(Shader& shader,const primordial::CameraPose& pose,float t,
                int width,int height,GLuint quad,
                glm::vec3 lookAt=glm::vec3(0.0f)) {
    // Do not alter pre-dawn camera evaluation, especially the protected
    // 18–22s opening. After 240s the native camera can track a hero galaxy.
    const glm::vec3 forward = t<=240.0f
        ? glm::normalize(-pose.position)
        : glm::normalize(lookAt-pose.position);
    const glm::vec3 right=glm::normalize(glm::cross(forward,glm::vec3(0,0,1)));
    const glm::vec3 up=glm::normalize(glm::cross(right,forward));
    shader.use();
    const GLuint p=shader.getID();
    const float aspect=float(width)/float(height);
    glUniform1f(glGetUniformLocation(p,"uTime"),t);
    glUniform3fv(glGetUniformLocation(p,"uCameraPos"),1,glm::value_ptr(pose.position));
    glUniform3fv(glGetUniformLocation(p,"uCameraForward"),1,glm::value_ptr(forward));
    glUniform3fv(glGetUniformLocation(p,"uCameraRight"),1,glm::value_ptr(right));
    glUniform3fv(glGetUniformLocation(p,"uCameraUp"),1,glm::value_ptr(up));
    glUniform1f(glGetUniformLocation(p,"uAspect"),aspect);
    glUniform1f(glGetUniformLocation(p,"uTanHalfFovY"),
                primordial::verticalTanHalfFov(pose,aspect));
    glBindVertexArray(quad);
    glDrawArrays(GL_TRIANGLE_STRIP,0,4);
    glBindVertexArray(0);
}

int main(int argc,char** argv) {
    film::RenderOptions options;
    try { options=film::parseOptions(argc,argv); }
    catch(const std::exception& e) { std::cerr<<"Invalid render options: "<<e.what()<<'\n'; return 2; }
    if(options.showHelp) {
        std::cout<<"Native C++17/OpenGL/GLSL universe, eight chapters, 300 seconds\n"
            <<"Still: --time 25 --fps 30 --width 480 --height 270 --output frame.png\n"
            <<"Or: --frame 751 --fps 30 --output frame.png\n"
            <<"Renderer identity: --renderer-info (hidden context, no scene render)\n"
            <<"Batch: --start-frame 1 --end-frame 9000 --fps 30 --width 640 --height 360 --raw-video -\n"
            <<"Batch stdout is top-down RGB24 only; diagnostics go to stderr.\n"
            <<"Frame numbers are inclusive, 1-indexed, t=(frame-1)/fps.\n"
            <<"Use scripts/render_film.py for chunking, validation and safe resume.\n";
        return 0;
    }
    // Keep the binary frame stream free of logging, including driver messages.
    if(options.batch) std::cout.rdbuf(std::cerr.rdbuf());
    if(!glfwInit()) { std::cerr<<"ERROR: GLFW initialization failed.\n"; return 1; }
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR,3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR,3);
    glfwWindowHint(GLFW_OPENGL_PROFILE,GLFW_OPENGL_CORE_PROFILE);
    if(options.capture) {
        glfwWindowHint(GLFW_VISIBLE,GLFW_FALSE);
        glfwWindowHint(GLFW_RESIZABLE,GLFW_FALSE);
    }
    GLFWwindow* window=glfwCreateWindow(options.width,options.height,
        "Primordial Universe | Native C++",nullptr,nullptr);
    if(!window) { glfwTerminate(); std::cerr<<"ERROR: Window creation failed.\n"; return 1; }
    glfwMakeContextCurrent(window);
    if(!gladLoadGL((GLADloadfunc)glfwGetProcAddress)) {
        glfwDestroyWindow(window); glfwTerminate();
        std::cerr<<"ERROR: GLAD initialization failed.\n"; return 1;
    }
    if(options.rendererInfo) {
        // Stable key/value protocol for checkpoint compatibility. No shaders,
        // HDR buffers, frame pixels or scene state are created by this query.
        std::cout<<"opengl_version="<<glGetString(GL_VERSION)
            <<"\nrenderer="<<glGetString(GL_RENDERER)
            <<"\nvendor="<<glGetString(GL_VENDOR)
            <<"\nshading_language_version="<<glGetString(GL_SHADING_LANGUAGE_VERSION)<<'\n';
        glfwDestroyWindow(window); glfwTerminate(); return 0;
    }
    glfwSetFramebufferSizeCallback(window,framebufferSizeCallback);
    glfwSwapInterval(options.capture?0:1);
    glEnable(GL_PROGRAM_POINT_SIZE);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA,GL_ONE);
    glDisable(GL_DEPTH_TEST);
    std::cout<<"OpenGL: "<<glGetString(GL_VERSION)<<"\nGPU: "<<glGetString(GL_RENDERER)
        <<"\nRenderer: native C++/GLSL, no pre-rendered video or Python frames\n";
    int result=0;
    try {
        const std::string root=PROJECT_ROOT;
        Shader composite(root+"/shaders/postprocess/screen.vert",root+"/shaders/postprocess/composite.frag");
        Shader primordial(root+"/shaders/postprocess/screen.vert",root+"/shaders/postprocess/primordial_volume.frag");
        Shader nasaOrigin(root+"/shaders/postprocess/screen.vert",root+"/shaders/postprocess/nasa_origin.frag");
        Shader evolution(root+"/shaders/postprocess/screen.vert",root+"/shaders/postprocess/cosmic_evolution.frag");
        cinematic::GalaxyCatalog deepField(root);
        int initialWidth=0,initialHeight=0;
        glfwGetFramebufferSize(window,&initialWidth,&initialHeight);
        // STAGE 7: physical output pixel dimensions, same HDR and bloom pipeline.
        HDRFramebuffer hdr(std::max(1,initialWidth),std::max(1,initialHeight));
        BloomEffect bloom(root+"/shaders/postprocess",std::max(1,initialWidth),std::max(1,initialHeight));
        const float quadVertices[]={-1,-1,0,0, 1,-1,1,0, -1,1,0,1, 1,1,1,1};
        GLuint quad=0,vbo=0;
        glGenVertexArrays(1,&quad); glGenBuffers(1,&vbo);
        glBindVertexArray(quad); glBindBuffer(GL_ARRAY_BUFFER,vbo);
        glBufferData(GL_ARRAY_BUFFER,sizeof(quadVertices),quadVertices,GL_STATIC_DRAW);
        glEnableVertexAttribArray(0); glVertexAttribPointer(0,2,GL_FLOAT,GL_FALSE,4*sizeof(float),(void*)0);
        glEnableVertexAttribArray(1); glVertexAttribPointer(1,2,GL_FLOAT,GL_FALSE,4*sizeof(float),(void*)(2*sizeof(float)));
        glBindBuffer(GL_ARRAY_BUFFER,0); glBindVertexArray(0);
        const double start=glfwGetTime();
        std::int64_t cursor=options.frame;
        while(!glfwWindowShouldClose(window)) {
            if(glfwGetKey(window,GLFW_KEY_ESCAPE)==GLFW_PRESS) break;
            // Every output frame is a pure function of its exact global time.
            const float t=static_cast<float>(options.batch?film::secondsForFrame(cursor,options.fps):
                (options.capture?options.timeSeconds:std::min(299.999,glfwGetTime()-start)));
            int width=0,height=0; glfwGetFramebufferSize(window,&width,&height);
            if(height==0) { glfwPollEvents(); continue; }
            if(options.capture&&(width!=options.width||height!=options.height))
                throw std::runtime_error("Framebuffer dimensions differ from requested capture dimensions");
            hdr.resize(width,height); bloom.resize(width,height); hdr.bind();
            glViewport(0,0,width,height);
            glClearColor(.002f,.001f,.008f,1); glClear(GL_COLOR_BUFFER_BIT);
            glDisable(GL_BLEND);
            // STAGES 1/4/6/8: procedural world medium, shading, bounded depth and
            // native fragment-ray transport. No M0 orange-particle placeholders.
            if(t<=56.0f) drawVolume(primordial,primordial::cameraAt(t),t,width,height,quad);
            if(t<18.0f) {
                // User-selected NASA 2007 opening: magenta-white ignition,
                // brief controlled brilliance and soft milk-grey transition.
                // Protected native opening 18–22s remains EXACTLY unchanged.
                glEnable(GL_BLEND);
                glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
                drawVolume(nasaOrigin,primordial::cameraAt(t),t,width,height,quad);
                glDisable(GL_BLEND);
                glBlendFunc(GL_SRC_ALPHA,GL_ONE);
            }
            if(t>45.0f) {
                glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
                drawVolume(evolution,cinematic::cameraAt(t),t,width,height,quad,
                           cinematic::targetAt(t));
                glDisable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA,GL_ONE);
            }
            // The NASA-2007-inspired cosmic dawn has thousands of small,
            // varied galaxies in a fixed 3D catalogue, not three luminous
            // spheres. This executes inside the native HDR pass.
            if(t>=240.0f)
                deepField.draw(t,cinematic::cameraAt(t),cinematic::targetAt(t),
                               width,height);
            HDRFramebuffer::unbind();
            const GLuint highlights=bloom.render(hdr.getColorTexture(),quad);
            glViewport(0,0,width,height); glDisable(GL_BLEND);
            glClearColor(0,0,0,1); glClear(GL_COLOR_BUFFER_BIT);
            // STAGE 9: unchanged scene-linear HDR, bloom, SDR tone mapping/gamma.
            composite.use();
            glActiveTexture(GL_TEXTURE0); glBindTexture(GL_TEXTURE_2D,hdr.getColorTexture());
            glActiveTexture(GL_TEXTURE1); glBindTexture(GL_TEXTURE_2D,highlights);
            glUniform1i(glGetUniformLocation(composite.getID(),"uScene"),0);
            glUniform1i(glGetUniformLocation(composite.getID(),"uBloomBlur"),1);
            glUniform1f(glGetUniformLocation(composite.getID(),"uBloomStrength"),1.2f);
            glUniform1f(glGetUniformLocation(composite.getID(),"uExposure"),1.0f);
            glBindVertexArray(quad); glDrawArrays(GL_TRIANGLE_STRIP,0,4); glBindVertexArray(0);
            glActiveTexture(GL_TEXTURE1); glBindTexture(GL_TEXTURE_2D,0);
            glActiveTexture(GL_TEXTURE0); glBindTexture(GL_TEXTURE_2D,0);
            glEnable(GL_BLEND);
            if(options.capture) {
                std::vector<std::uint8_t> pixels(std::size_t(width)*height*3u);
                glFinish(); glPixelStorei(GL_PACK_ALIGNMENT,1); glReadBuffer(GL_BACK);
                glReadPixels(0,0,width,height,GL_RGB,GL_UNSIGNED_BYTE,pixels.data());
                if(glGetError()!=GL_NO_ERROR) throw std::runtime_error("OpenGL readback failed");
                if(options.batch) {
                    const std::size_t stride=std::size_t(width)*3u;
                    for(int y=height-1;y>=0;--y)
                        if(std::fwrite(pixels.data()+std::size_t(y)*stride,1,stride,stdout)!=stride)
                            throw std::runtime_error("Native RGB24 stream write failed");
                    if(cursor==options.frame||cursor%options.fps==0||cursor==options.endFrame)
                        std::cerr<<"Rendered frame "<<cursor<<" t="<<t<<"s\n";
                    if(cursor==options.endFrame) break;
                    ++cursor;
                } else {
                    png::writeRgbBottomUp(options.output,width,height,pixels);
                    std::cout<<"Native C++ PNG: "<<options.output<<" ("<<width<<"x"<<height<<")\n";
                    break;
                }
            } else glfwSwapBuffers(window);
            glfwPollEvents();
        }
        if(options.batch) {
            if(std::fflush(stdout)!=0) throw std::runtime_error("Native RGB24 stream flush failed");
            if(cursor!=options.endFrame) throw std::runtime_error("Capture interrupted before requested last frame");
            std::cerr<<"Completed "<<(options.endFrame-options.frame+1)<<" native frames in "
                     <<(glfwGetTime()-start)<<" seconds\n";
        }
        glDeleteBuffers(1,&vbo); glDeleteVertexArrays(1,&quad);
    } catch(const std::exception& e) { std::cerr<<"ERROR: "<<e.what()<<'\n'; result=1; }
    glfwDestroyWindow(window); glfwTerminate(); return result;
}
