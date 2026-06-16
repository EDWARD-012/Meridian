import { Suspense } from 'react'
import { Canvas } from '@react-three/fiber'
import { Float, MeshDistortMaterial } from '@react-three/drei'

function Shape() {
  return (
    <Float speed={1.5} rotationIntensity={0.6} floatIntensity={0.8}>
      <mesh scale={1.4}>
        <icosahedronGeometry args={[1, 1]} />
        <MeshDistortMaterial
          color="#d4a574"
          roughness={0.35}
          metalness={0.6}
          distort={0.25}
          speed={2}
        />
      </mesh>
    </Float>
  )
}

export default function Hero3D() {
  return (
    <div className="hero-3d">
      <Canvas camera={{ position: [0, 0, 4], fov: 45 }}>
        <ambientLight intensity={0.4} />
        <directionalLight position={[5, 5, 5]} intensity={1.2} />
        <pointLight position={[-3, -2, 2]} color="#d4a574" intensity={0.5} />
        <Suspense fallback={null}>
          <Shape />
        </Suspense>
      </Canvas>
    </div>
  )
}
